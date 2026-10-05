import Vision
import AppKit

// macOS Vision framework OCR — zh-Hans + en-US, accurate level.
// Usage: swift ocr.swift <image-path>
let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path),
      let cgImage = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("cannot load image")
    exit(1)
}
let request = VNRecognizeTextRequest { req, err in
    guard let results = req.results as? [VNRecognizedTextObservation] else { return }
    for obs in results {
        if let top = obs.topCandidates(1).first {
            print(top.string)
        }
    }
}
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.recognitionLevel = .accurate
let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try? handler.perform([request])
