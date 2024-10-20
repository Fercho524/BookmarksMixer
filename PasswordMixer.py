import os
import pandas as pd


def read_csv_files_from_directory(directory_path):
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    dataframes = {}

    for csv_file in csv_files:
        file_path = os.path.join(directory_path, csv_file)
        try:
            df = pd.read_csv(file_path)
            dataframes[csv_file] = df
            print(f'Archivo {csv_file} leído correctamente.')
        except Exception as e:
            print(f'Error al leer {csv_file}: {e}')

    return dataframes


def merge_all_passwords(directory):
    dfs = read_csv_files_from_directory(directory)

    for filename, df in dfs.items():
        print(f'\nColumnas {filename}:')
        print(df.columns)

    concatenated_df = pd.concat(dfs.values(), ignore_index=True, sort=False)

     # Ordenar los valores por URL
    concatenated_df = concatenated_df.sort_values("url")

    # Eliminar filas duplicadas, manteniendo registros únicos basados en la combinación de 'url', 'usuario' y 'contraseña'
    unique_df = concatenated_df.drop_duplicates(subset=['url', 'username', 'password'])

    return unique_df
    # Guardar el dataframe final en un archivo CSV
    



if __name__ == "__main__":
    directory = input("Ingresa un directorio con archivos csv")
    dest_file = input("Ingresa la ruta del archivo final")

    unique_df = merge_all_passwords(directory)
    unique_df.to_csv(dest_file, index=False)
