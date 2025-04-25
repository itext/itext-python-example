#!/usr/bin/env python3
import init_itextpy_package
import init_stubs_package
import patch_itext_binaries


def main() -> int:
    exit_code = init_itextpy_package.run()
    if exit_code == 0:
        exit_code = patch_itext_binaries.run()
    if exit_code == 0:
        exit_code = init_stubs_package.run()
    return exit_code


if __name__ == '__main__':
    import sys
    sys.exit(main())
