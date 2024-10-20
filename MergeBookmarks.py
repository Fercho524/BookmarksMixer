import os
import sys
import json


def parseHTML(file_path):
    with open(file_path, encoding='utf-8', mode='r') as fo:
        original = fo.read()

    parsed = {}
    current_location = []
    current_location_name = []
    current_index = 0
    header = original.find("<H1>")
    if header > -1:
        ender = original.find("</H1>")
        parsed[original[header+4:ender]] = {"link": []}
        folder_begin = original.find("<DL><p>")
        if folder_begin > -1:
            current_location.append(parsed[original[header+4:ender]])
            current_location_name.append(original[header+4:ender])
        original = original[folder_begin+7:]

    block = False
    original_length = len(original)

    while current_index + 1 < original_length:
        folder_title_header = original.find("<DT><H3", current_index)
        folder_title_ender = original.find("</H3>", current_index)
        folder_header = original.find("<DL><p>", current_index)
        folder_ender = original.find("</DL><p>", current_index)
        bookmark_header = original.find("<DT><A", current_index)
        bookmark_ender = original.find("</A>", current_index)

        lists = [folder_title_header, folder_title_ender, folder_header, folder_ender, bookmark_header, bookmark_ender]
        for i in range(6):
            # Prevent the min() from choosing the non-existent value -1
            if lists[i] == -1:
                lists[i] = original_length + 1

        nearest_element = min(lists)

        if lists[3] + 8 >= original_length:  # Escape the loop to prevent looping over -1 values
            break

        if nearest_element == folder_title_header and not block:
            if not folder_title_ender > -1 and not folder_title_header + 1 > original_length:
                block = True
                continue
            folder_title_header = original.find(">", folder_title_header + 7)
            upper_folder = current_location[-1]
            upper_folder[original[folder_title_header+1:folder_title_ender]] = {"link": []}
            current_location.append(upper_folder[original[folder_title_header+1:folder_title_ender]])
            current_location_name.append(original[folder_title_header+1:folder_title_ender])
            current_index = folder_title_ender + 5
            #print("Working on: {}".format("/".join(current_location_name)))
            continue

        if nearest_element == folder_header:
            current_index = folder_header + 7
            continue

        if nearest_element == folder_ender and folder_ender + 8 < original_length:
            current_location.pop()
            current_location_name.pop()
            current_index = folder_ender + 8
            continue

        if nearest_element == bookmark_header:
            link_header = original.find("HREF=", bookmark_header)
            if link_header > -1:
                link_ender = original.find('"', link_header + 6)
                bookmark_title_header = original.find(">", link_header)
                current_location[-1]["link"].append([original[link_header+6:link_ender], original[bookmark_title_header+1:bookmark_ender]])
                current_index = bookmark_ender + 4
            continue
    #print("Finished parsing bookmarks!")
    return parsed.copy()


def writeJSON(result, path_to_save=None, indent=4, encoding="utf-8", mode="w"):
    if not path_to_save:
        #print("JSON saving path not found! Skipping...")
        return 1
    with open(path_to_save, encoding=encoding, mode=mode) as files:
        json.dump(result, files, indent=indent, ensure_ascii=False)
    #print(f"JSON file written to path: {path_to_save}")


def get_html_files(directory):
    # Lista para almacenar los archivos .html
    html_files = []

    # Recorrer el directorio
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            html_files.append(filename)
            print(filename)
   
    return html_files


def merge_bookmarks(folder1, folder2):
    """
    Fusiona el contenido de folder2 en folder1 siguiendo la lógica de fusión de carpetas:
    - Carpetas con el mismo nombre se mezclan.
    - Enlaces duplicados se omiten (comparación por URL).
    """
    
    for key, value in folder2.items():
        if key == "link":
            # Fusionar los enlaces, evitando duplicados basados en la URL (primer elemento de cada lista)
            existing_links = set(tuple(link) for link in folder1.get("link", []))
            new_links = set(tuple(link) for link in value)
            
            # Solo añadimos los nuevos enlaces que no estén ya en folder1
            merged_links = list(existing_links.union(new_links))
            folder1["link"] = merged_links
        
        else:
            # Si la carpeta ya existe en folder1, se fusiona de manera recursiva
            if key in folder1:
                merge_bookmarks(folder1[key], value)
            else:
                # Si la carpeta no existe, simplemente la añadimos
                folder1[key] = value


def merge_all_bookmarks(bookmarks1, bookmarks2):
    """
    Fusiona dos estructuras de marcadores en una sola.
    bookmarks1 y bookmarks2 son diccionarios que representan la estructura del árbol de marcadores.
    """
    merge_bookmarks(bookmarks1, bookmarks2)
    return bookmarks1


def merge_multiple_html_files(directory, output_file):
    # Obtener todos los archivos HTML en el directorio
    html_files = get_html_files(directory)

    if not html_files:
        print("No se encontraron archivos HTML en el directorio.")
        return

    # Iniciar con una copia del primer archivo de favoritos
    merged_bookmarks = parseHTML(html_files[0])
    print(f"Archivo {html_files[0]} cargado como base.")

    # Iterar sobre los archivos restantes y mezclarlos
    for html_file in html_files[1:]:
        print(f"Mezclando archivo {html_file}...")
        next_bookmarks = parseHTML(html_file)
        merged_bookmarks = merge_all_bookmarks(merged_bookmarks, next_bookmarks)

    # Guardar el resultado final en el archivo JSON
    writeJSON(merged_bookmarks, output_file)
    print(f"Todos los favoritos se han mezclado y guardado en {output_file}.")


if __name__ == "__main__":
    directory = input("Introduce el directorio donde están los archivos HTML de favoritos: ")
    output_file = input("Introduce la ruta donde guardar el archivo JSON mezclado: ")

    merge_multiple_html_files(directory, output_file)