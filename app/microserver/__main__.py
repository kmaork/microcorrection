from os import getenv

from microserver.views import app


# TODO: tests for all features
# TODO: tests for more levels
# TODO: save state in redis to allow workers
# TODO: logs and traces
# TODO: support insncount by changing emulator
# TODO: add backwards step
# TODO: try using gdb disassembler instead of naken asm?

# TODO: sometimes when running tests there is a race that kills an emulator while it is being used
def main():
    app.run(host='0.0.0.0',
            port=int(getenv('PORT', '8000')),
            debug=True, use_reloader=True, threaded=True)


if __name__ == '__main__':
    main()
