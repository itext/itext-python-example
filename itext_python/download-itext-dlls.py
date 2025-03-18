import requests
import zipfile
import io
import os
from typing import List, Tuple

itext_version = "9.1.0"
dll_path = "dlls"


def download_and_extract_dll(url: str, dll_list: List[Tuple[str, str]]):
    """
    Downloads a NuGet package, extracts a specific DLL,
    and saves it to the specified path.
    """
    try:
        # 1. Download the NuGet package
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # 2. Extract the DLL from the NuGet package (ZIP file)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for dll_in_zip, output_path in dll_list:
                try:
                    dll_data = z.read(dll_in_zip)

                    # 3. Save the DLL to the specified path
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "wb") as dll_file:
                        dll_file.write(dll_data)
                    print(f"Extracted: {dll_in_zip} -> {output_path}")
                except KeyError:
                    print(f"Error: DLL '{dll_in_zip}' not found in NuGet package.")
                except Exception as e:
                    print(f"Error extracting {dll_in_zip}: {str(e)}")

    except requests.exceptions.RequestException as e:
        print(f"Download error: {e}")
    except zipfile.BadZipFile:
        print("Error: Invalid NuGet package (ZIP file).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


nuget_package_url = "https://www.nuget.org/api/v2/package/itext/" + itext_version

dll_list = [
    ("lib/netstandard2.0/itext.kernel.dll", dll_path + "/itext.kernel.dll"),
    ("lib/netstandard2.0/itext.io.dll", dll_path + "/itext.io.dll"),
    ("lib/netstandard2.0/itext.layout.dll", dll_path + "/itext.layout.dll"),
    (
        "lib/netstandard2.0/itext.bouncy-castle-connector.dll",
        dll_path + "/itext.bouncy-castle-connector.dll",
    ),
    # Add more DLLs as needed
]

download_and_extract_dll(nuget_package_url, dll_list)

nuget_package_url = (
    "https://www.nuget.org/api/v2/package/itext.commons/" + itext_version
)

dll_list = [
    ("lib/netstandard2.0/itext.commons.dll", dll_path + "/itext.commons.dll"),
]

download_and_extract_dll(nuget_package_url, dll_list)

nuget_package_url = (
    "https://www.nuget.org/api/v2/package/itext.bouncy-castle-adapter/" + itext_version
)

dll_list = [
    (
        "lib/netstandard2.0/itext.bouncy-castle-adapter.dll",
        dll_path + "/itext.bouncy-castle-adapter.dll",
    ),
]

download_and_extract_dll(nuget_package_url, dll_list)
