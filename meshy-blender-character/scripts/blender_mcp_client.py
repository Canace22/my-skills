"""Actual stdio MCP client. Requires the mcp package and a running local Blender add-on."""
import argparse
import asyncio
import os
from pathlib import Path
import shutil


async def run(args):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    uvx = shutil.which('uvx')
    if not uvx:
        raise SystemExit('uvx was not found; use the configured MCP tools or install the required runtime.')
    prompt = Path(args.prompt_file).read_text().strip()
    if not prompt:
        raise SystemExit('The prompt file must contain the user request.')
    arguments = {'user_prompt': prompt}
    tool = 'get_scene_info'
    if args.script:
        script = Path(args.script).resolve()
        arguments['code'] = '__file__ = ' + repr(str(script)) + '\n' + script.read_text()
        tool = 'execute_blender_code'
    parameters = StdioServerParameters(command=uvx,
        args=['--from', args.package, 'blender-mcp'],
        env={**os.environ, 'BLENDER_HOST': '127.0.0.1',
             'BLENDER_PORT': str(args.port), 'DISABLE_TELEMETRY': 'true'})
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            for block in result.content:
                if hasattr(block, 'text'):
                    print(block.text)
            if result.isError:
                raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompt-file', required=True, help='UTF-8 file containing the user request verbatim')
    parser.add_argument('--script', help='Local bpy script; omitted means read-only scene inspection')
    parser.add_argument('--port', type=int, default=9876)
    parser.add_argument('--package', default='blender-mcp==1.9.1',
                        help='Compatible official package; default is the tested version')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    asyncio.run(run(args))


if __name__ == '__main__':
    main()
