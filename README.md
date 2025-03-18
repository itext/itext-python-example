# Intro

This aims to create a pip package for iText 9 distribution


# Build 

To build the package, just run:

```
python -m build
```

which should create a:

```
./dist/itext_python-9.1.0-py3-none-any.whl
```

file, that then you can install by using

```
pip install ./dist/itext_python-9.1.0-py3-none-any.whl
```


# Limitations

* You still need to download the DDLs file yourself (TODO)
* The way the packages are exposed, everything is under the same namespace, which can be confusing


# Needed DLLs

* BouncyCastle.Cryptography.dll
* Microsoft.DotNet.PlatformAbstractions.dll
* Microsoft.Extensions.DependencyModel.dll
* Microsoft.Extensions.Logging.Abstractions.dll
* Microsoft.Extensions.Logging.dll
* Microsoft.Extensions.Options.dll
* itext.bouncy-castle-adapter.dll
* itext.bouncy-castle-connector.dll
* itext.commons.dll
* itext.io.dll
* itext.kernel.dll
* itext.layout.dll
