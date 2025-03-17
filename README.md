# Intro

Just showcasing how to use iText 9 in a Python environment


# Installation

I've done this on a Mac environment, using Python 3.13.2

You will basically need [pythonnet](https://pypi.org/project/pythonnet/)
```
pip install -r requirements.txt
```

and a .NET running environment
```
brew install mono
```


And then you just need all the required .dlls which you will place on this folder. You can get away with just:

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


