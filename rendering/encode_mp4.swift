// macOS: encode a numbered JPEG/PNG sequence as an H.264 MP4, without audio.
// Run from this folder after rendering:
//   swift encode_mp4.swift rendered-frames warm-shelf-v4.mp4 192 24
//   swift encode_mp4.swift rendered-frames organizer.mp4 144 24 20
// Optional arguments default to 192 frames, 24 fps and 8 Mbps.
// Bitrate is a whole number from 1 through 1000 Mbps; 20 is useful for finer detail.
// Existing output files are preserved. Validation also writes preview frames
// and a JSON report beside the input frames, in an encoded-checks directory.

import Foundation
import AVFoundation
import CoreGraphics
import CoreVideo
import CoreMedia
import ImageIO
import UniformTypeIdentifiers

enum VideoError: Error, CustomStringConvertible {
    case message(String)
    var description: String { switch self { case let .message(message): return message } }
}

func check(_ condition: Bool, _ message: String) throws {
    if !condition { throw VideoError.message(message) }
}

func positiveInteger(_ arguments: [String], at index: Int, fallback: Int, name: String) throws -> Int {
    guard index < arguments.count else { return fallback }
    guard let value = Int(arguments[index]), value > 0 else {
        throw VideoError.message("\(name) must be a positive integer")
    }
    return value
}

func readImage(_ url: URL) throws -> CGImage {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw VideoError.message("Cannot read frame: \(url.path)")
    }
    return image
}

func writeJPEG(_ image: CGImage, to url: URL) throws {
    guard let destination = CGImageDestinationCreateWithURL(url as CFURL, UTType.jpeg.identifier as CFString, 1, nil) else {
        throw VideoError.message("Cannot create preview: \(url.path)")
    }
    CGImageDestinationAddImage(destination, image, [kCGImageDestinationLossyCompressionQuality: 0.94] as CFDictionary)
    try check(CGImageDestinationFinalize(destination), "Cannot save preview: \(url.path)")
}

func verify(_ output: URL, expectedCount: Int, fps: Int32, previewDirectory: URL) throws {
    let asset = AVURLAsset(url: output)
    guard let track = asset.tracks(withMediaType: .video).first else { throw VideoError.message("Encoded video has no video track") }
    let duration = CMTimeGetSeconds(asset.duration)
    try check(abs(duration - Double(expectedCount)/Double(fps)) < 0.02, "Unexpected duration: \(duration)")
    try check(asset.tracks(withMediaType: .audio).isEmpty, "Unexpected audio track")
    let reader = try AVAssetReader(asset: asset)
    let trackOutput = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
    reader.add(trackOutput)
    try check(reader.startReading(), "Cannot decode encoded video: \(reader.error?.localizedDescription ?? "unknown error")")
    var count = 0
    while let sample = trackOutput.copyNextSampleBuffer() {
        try check(CMSampleBufferGetImageBuffer(sample) != nil, "Decoded sample has no image")
        count += 1
    }
    try check(reader.status == .completed, "Decode failed: \(reader.error?.localizedDescription ?? "unknown error")")
    try check(count == expectedCount, "Expected \(expectedCount) frames, decoded \(count)")
    let generator = AVAssetImageGenerator(asset: asset)
    generator.appliesPreferredTrackTransform = true
    generator.requestedTimeToleranceBefore = .zero
    generator.requestedTimeToleranceAfter = .zero
    try FileManager.default.createDirectory(at: previewDirectory, withIntermediateDirectories: true)
    for index in [0, expectedCount/2, expectedCount-1] {
        var actual = CMTime.zero
        let image = try generator.copyCGImage(at: CMTime(value: Int64(index), timescale: fps), actualTime: &actual)
        try writeJPEG(image, to: previewDirectory.appendingPathComponent(String(format: "encoded-%04d.jpg", index+1)))
    }
    let report: [String: Any] = [
        "output": output.path,
        "duration_seconds": duration,
        "decoded_frame_count": count,
        "nominal_fps": track.nominalFrameRate,
        "width": Int(track.naturalSize.width),
        "height": Int(track.naturalSize.height),
        "audio_track_count": asset.tracks(withMediaType: .audio).count,
        "file_bytes": try output.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0,
        "previews": previewDirectory.path
    ]
    let data = try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys])
    try data.write(to: previewDirectory.appendingPathComponent("video-verification.json"))
    print(String(data: data, encoding: .utf8)!)
}

func main() throws {
    let arguments = Array(CommandLine.arguments.dropFirst())
    try check((2...5).contains(arguments.count), "Usage: swift encode_mp4.swift FRAME_DIRECTORY OUTPUT.mp4 [EXPECTED_FRAMES=192] [FPS=24] [BITRATE_MBPS=8]")
    let directory = URL(fileURLWithPath: arguments[0], isDirectory: true)
    let output = URL(fileURLWithPath: arguments[1])
    let expectedCount = try positiveInteger(arguments, at: 2, fallback: 192, name: "Frame count")
    let fpsValue = try positiveInteger(arguments, at: 3, fallback: 24, name: "FPS")
    try check(fpsValue <= Int(Int32.max), "FPS exceeds the supported integer range")
    let fps = Int32(fpsValue)
    let bitrateMbps = try positiveInteger(arguments, at: 4, fallback: 8, name: "Bitrate in Mbps")
    try check(bitrateMbps <= 1000, "Bitrate must be between 1 and 1000 Mbps")
    let files = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        .filter { ["jpg", "jpeg", "png"].contains($0.pathExtension.lowercased()) }
        .sorted { $0.lastPathComponent < $1.lastPathComponent }
    try check(files.count == expectedCount, "Expected \(expectedCount) source frames, found \(files.count). Wait for rendering to finish.")
    let firstImage = try readImage(files[0])
    let width = firstImage.width
    let height = firstImage.height
    try check(width % 2 == 0 && height % 2 == 0, "H.264 frame dimensions must be even")
    try FileManager.default.createDirectory(at: output.deletingLastPathComponent(), withIntermediateDirectories: true)
    try check(!FileManager.default.fileExists(atPath: output.path), "Output already exists; choose a new path or explicitly remove it first")
    let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
    writer.shouldOptimizeForNetworkUse = true
    let compression: [String: Any] = [
        AVVideoAverageBitRateKey: bitrateMbps * 1_000_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
        AVVideoMaxKeyFrameIntervalKey: Int(fps),
        AVVideoAllowFrameReorderingKey: false
    ]
    let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
        AVVideoCodecKey: AVVideoCodecType.h264,
        AVVideoWidthKey: width,
        AVVideoHeightKey: height,
        AVVideoCompressionPropertiesKey: compression
    ])
    input.expectsMediaDataInRealTime = false
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
        kCVPixelBufferWidthKey as String: width,
        kCVPixelBufferHeightKey as String: height,
        kCVPixelBufferCGImageCompatibilityKey as String: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey as String: true
    ])
    try check(writer.canAdd(input), "Video writer cannot accept H.264 settings")
    writer.add(input)
    try check(writer.startWriting(), "Cannot start encoding: \(writer.error?.localizedDescription ?? "unknown error")")
    writer.startSession(atSourceTime: .zero)
    guard let pool = adaptor.pixelBufferPool else { throw VideoError.message("No pixel buffer pool") }
    let colorspace = CGColorSpaceCreateDeviceRGB()
    for (index, file) in files.enumerated() {
        try autoreleasepool {
            let image = try readImage(file)
            try check(image.width == width && image.height == height, "Frame size mismatch: \(file.lastPathComponent)")
            var optionalBuffer: CVPixelBuffer?
            try check(CVPixelBufferPoolCreatePixelBuffer(nil, pool, &optionalBuffer) == kCVReturnSuccess, "Cannot allocate frame buffer")
            guard let buffer = optionalBuffer else { throw VideoError.message("Missing frame buffer") }
            CVPixelBufferLockBaseAddress(buffer, [])
            defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
            guard let context = CGContext(data: CVPixelBufferGetBaseAddress(buffer), width: width, height: height,
                bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(buffer), space: colorspace,
                bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue) else {
                throw VideoError.message("Cannot create frame drawing context")
            }
            context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
            let readyDeadline = Date().addingTimeInterval(30)
            while !input.isReadyForMoreMediaData {
                try check(writer.status == .writing, "Encoder failed: \(writer.error?.localizedDescription ?? "unknown error")")
                try check(Date() < readyDeadline, "Encoder stopped accepting frames")
                Thread.sleep(forTimeInterval: 0.005)
            }
            try check(adaptor.append(buffer, withPresentationTime: CMTime(value: Int64(index), timescale: fps)),
                "Cannot append frame \(index+1): \(writer.error?.localizedDescription ?? "unknown error")")
        }
    }
    input.markAsFinished()
    writer.endSession(atSourceTime: CMTime(value: Int64(files.count), timescale: fps))
    let completion = DispatchSemaphore(value: 0)
    writer.finishWriting { completion.signal() }
    try check(completion.wait(timeout: .now() + 60) == .success, "Encoder finalization timed out")
    try check(writer.status == .completed, "Encoder failed: \(writer.error?.localizedDescription ?? "unknown error")")
    try verify(output, expectedCount: expectedCount, fps: fps, previewDirectory: directory.deletingLastPathComponent().appendingPathComponent("encoded-checks"))
}

do { try main() } catch { fputs("ERROR: \(error)\n", stderr); exit(1) }
