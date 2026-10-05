"""Read GLB metadata without Blender, a browser, network access or third-party packages."""
import argparse
import json
from pathlib import Path
import struct


def read_glb(path):
    data = Path(path).read_bytes()
    if len(data) < 20:
        raise ValueError('File is too short to be a GLB')
    magic, version, length = struct.unpack_from('<4sII', data)
    if magic != b'glTF' or version != 2 or length != len(data):
        raise ValueError('Invalid GLB header or truncated file')
    offset = 12
    document = None
    while offset < length:
        if offset + 8 > length:
            raise ValueError('Truncated chunk header')
        size, kind = struct.unpack_from('<II', data, offset)
        offset += 8
        if size % 4 or offset + size > length:
            raise ValueError('Invalid chunk length')
        if document is None:
            if kind != 0x4E4F534A:
                raise ValueError('The first GLB chunk must contain JSON')
            document = json.loads(data[offset:offset + size])
        offset += size
    if not isinstance(document, dict) or document.get('asset', {}).get('version') != '2.0':
        raise ValueError('Missing glTF 2.0 asset metadata')
    return document, length


def inspect(path):
    doc, size = read_glb(path)
    accessors = doc.get('accessors', [])
    triangles = 0
    unknown = 0
    for mesh in doc.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            index = primitive.get('indices', primitive.get('attributes', {}).get('POSITION'))
            mode = primitive.get('mode', 4)
            if index is None or not 0 <= index < len(accessors):
                unknown += 1
                continue
            count = accessors[index]['count']
            if mode == 4:
                triangles += count // 3
            elif mode in (5, 6):
                triangles += max(0, count - 2)
            else:
                unknown += 1
    materials = []
    for material in doc.get('materials', []):
        extensions = material.get('extensions', {})
        pbr = material.get('pbrMetallicRoughness', {})
        materials.append({
            'name': material.get('name'), 'alpha_mode': material.get('alphaMode', 'OPAQUE'),
            'emissive_factor': material.get('emissiveFactor', [0, 0, 0]),
            'has_emissive_texture': 'emissiveTexture' in material,
            'unlit': 'KHR_materials_unlit' in extensions,
            'metallic': pbr.get('metallicFactor', 1), 'roughness': pbr.get('roughnessFactor', 1),
            'specular': extensions.get('KHR_materials_specular'),
        })
    return {
        'file': str(Path(path).resolve()), 'bytes': size,
        'meshes': len(doc.get('meshes', [])), 'skins': len(doc.get('skins', [])),
        'joint_references': sum(len(skin.get('joints', [])) for skin in doc.get('skins', [])),
        'animations': [animation.get('name', '') for animation in doc.get('animations', [])],
        'geometry_triangles_estimate': triangles, 'unestimated_primitives': unknown,
        'images': len(doc.get('images', [])), 'materials': materials,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    parser.add_argument('--require-skin', action='store_true')
    parser.add_argument('--require-clips', nargs='+', default=[])
    args = parser.parse_args()
    try:
        report = inspect(args.file)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.require_skin and not report['skins']:
            raise ValueError('Expected at least one skin')
        missing = set(args.require_clips) - set(report['animations'])
        if missing:
            raise ValueError('Missing animation clips: ' + ', '.join(sorted(missing)))
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
