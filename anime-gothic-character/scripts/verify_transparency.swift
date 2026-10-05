#!/usr/bin/env swift

import CoreGraphics
import Foundation
import ImageIO

guard CommandLine.arguments.count == 2 else {
    fputs("usage: verify_transparency.swift image.png\n", stderr)
    exit(2)
}

let imageURL = URL(fileURLWithPath: CommandLine.arguments[1]) as CFURL
guard
    let source = CGImageSourceCreateWithURL(imageURL, nil),
    let image = CGImageSourceCreateImageAtIndex(source, 0, nil)
else {
    fputs("FAIL: could not read image\n", stderr)
    exit(3)
}

let alphaInfo = image.alphaInfo
let noAlphaKinds: [CGImageAlphaInfo] = [.none, .noneSkipFirst, .noneSkipLast]
guard !noAlphaKinds.contains(alphaInfo) else {
    fputs("FAIL: image has no alpha channel\n", stderr)
    exit(4)
}

let width = image.width
let height = image.height
let bytesPerPixel = 4
let bytesPerRow = width * bytesPerPixel
var pixels = [UInt8](repeating: 0, count: height * bytesPerRow)

guard
    let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
    let context = CGContext(
        data: &pixels,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: bytesPerRow,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue |
            CGBitmapInfo.byteOrder32Big.rawValue
    )
else {
    fputs("FAIL: could not create RGBA context\n", stderr)
    exit(5)
}

context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))

var transparent = 0
var opaque = 0
for offset in stride(from: 3, to: pixels.count, by: bytesPerPixel) {
    let alpha = pixels[offset]
    if alpha <= 5 { transparent += 1 }
    if alpha >= 250 { opaque += 1 }
}

let total = width * height
let transparentRatio = Double(transparent) / Double(total)
let opaqueRatio = Double(opaque) / Double(total)
let cornerOffsets = [
    3,
    (width - 1) * bytesPerPixel + 3,
    (height - 1) * bytesPerRow + 3,
    (height - 1) * bytesPerRow + (width - 1) * bytesPerPixel + 3,
]
let transparentCorners = cornerOffsets.allSatisfy { pixels[$0] <= 5 }

guard transparentRatio >= 0.05 else {
    fputs("FAIL: fewer than 5% of pixels are transparent\n", stderr)
    exit(6)
}
guard opaqueRatio >= 0.01 else {
    fputs("FAIL: image has no substantial opaque subject\n", stderr)
    exit(7)
}
guard transparentCorners else {
    fputs("FAIL: one or more corners are opaque\n", stderr)
    exit(8)
}

print(String(
    format: "PASS: %dx%d RGBA, %.1f%% transparent, %.1f%% opaque, corners transparent",
    width,
    height,
    transparentRatio * 100,
    opaqueRatio * 100
))
