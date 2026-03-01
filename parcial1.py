import csv, math
# Matriz U -> Afinidad usuarios x géneros 
usuarios = []
generos = []
matriz_U = []

with open("afinidad_usuarios.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i == 0:
            generos = [col for col in row.keys() if col not in ("ID", "Usuario")]
        usuarios.append(row["Usuario"])
        matriz_U.append([int(row[g]) for g in generos])

# Matriz G -> Coincidencia géneros x películas 
peliculas = []
generos_G = []
matriz_G = []
with open("coincidencia_generos_peliculas.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i == 0:
            peliculas = [col for col in row.keys() if col != "Genero"]
        generos_G.append(row["Genero"])
        matriz_G.append([float(row[p]) for p in peliculas])

# ─────────────────────────────────────────────────────────────────
# Crear Matriz R resultante -> R[i][k] = suma de U[i][j] * G[j][k] 

filas_U = len(matriz_U)    # 100
cols_G  = len(matriz_G[0]) # 50
cols_U  = len(matriz_U[0]) # 5

matriz_R = [[0.0] * cols_G for _ in range(filas_U)]

for i in range(filas_U):
    for k in range(cols_G):
        for j in range(cols_U):
            matriz_R[i][k] += matriz_U[i][j] * matriz_G[j][k]

# ─────────────────────────────────────────────────────────────────
# Normalizar R a para que los resultados sean de 1 a 10
max_real = 0.0
for i in range(filas_U):
    for k in range(cols_G):
        if matriz_R[i][k] > max_real:
            max_real = matriz_R[i][k]

for i in range(filas_U):
    for k in range(cols_G):
        matriz_R[i][k] = round((matriz_R[i][k] / max_real) * 10, 2)


# ───────────────────────Metodos para el menu───────────────────────────────────
def merge_sort_desc(lista): # MERGE SORT para ordenar las mejores del top peliculas/generos de mayor a menor
    if len(lista) <= 1:
        return lista

    mitad = len(lista) // 2
    izquierda = merge_sort_desc(lista[:mitad])
    derecha = merge_sort_desc(lista[mitad:])

    return merge_desc(izquierda, derecha)


def merge_desc(izquierda, derecha):
    resultado = []
    i = j = 0

    while i < len(izquierda) and j < len(derecha):
        if izquierda[i][1] > derecha[j][1]:  # ordenar por el segundo elemento
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1

    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])

    return resultado
# ─────────────────────────────────────────────────────────────────
def mostrar_recomendaciones(indice_usuario, top_n):
    nombre   = usuarios[indice_usuario]
    puntajes = matriz_R[indice_usuario]

    pares = []
    for k in range(len(puntajes)):
        pares.append((k, puntajes[k]))

    pares = merge_sort_desc(pares)

    print("\n Top " + str(top_n) + " recomendaciones para " + nombre + ":")
    print("  #    Pelicula                        Puntaje")
    print("  " + "-" * 44)
    for rank, (idx, punt) in enumerate(pares[:top_n], 1):
        print("  " + str(rank) + "    " + peliculas[idx] + "    " + str(round(punt, 2)))
# ─────────────────────────────────────────────────────────────────
def similitud_coseno(fila_a, fila_b):  #para cualcular los usuarios mas similares
    dot   = sum(a * b for a, b in zip(fila_a, fila_b))
    mag_a = math.sqrt(sum(a ** 2 for a in fila_a))
    mag_b = math.sqrt(sum(b ** 2 for b in fila_b))
    return dot / (mag_a * mag_b)

# ─────────────────────────────────────────────────────────────────
def usuarios_similares(nombre_buscar, top_n):
    idx = next((i for i, u in enumerate(usuarios) if u.lower() == nombre_buscar.lower()), None)
    if idx is None:
        print(f" Usuario '{nombre_buscar}' no encontrado.")
        return

    similitudes = []
    for j in range(len(usuarios)):
        if j == idx:
            continue
        sim = similitud_coseno(matriz_R[idx], matriz_R[j])
        similitudes.append((j, sim))
    similitudes = merge_sort_desc(similitudes)

    print(f"\n Usuarios más similares a {usuarios[idx]}:")
    print(f"  {'#':<4} {'Usuario':<15} {'Similitud':>10}")
    print(f"  {'-'*30}")
    for rank, (j, sim) in enumerate(similitudes[:top_n], 1):
        print(f"  {rank:<4} {usuarios[j]:<15} {round(sim, 4):>10}")
# ─────────────────────────────────────────────────────────────────
def peliculas_populares_por_genero(top_n):
    print(f"\n Top {top_n} películas más populares por género:")
    print(f"  (basado en afinidad promedio de los {len(usuarios)} usuarios)\n")

    for j, genero in enumerate(generos_G):
        puntajes = []
        for k in range(cols_G):
            promedio_usuarios = sum(matriz_R[i][k] for i in range(filas_U)) / filas_U
            peso_genero = matriz_G[j][k]
            puntaje = promedio_usuarios * peso_genero
            puntajes.append((k, puntaje))

        puntajes = merge_sort_desc(puntajes)

        print(f"   Género: {genero}")
        print(f"  {'#':<4} {'Película':<30} {'Puntaje':>10}")
        print(f"  {'-'*46}")
        for rank, (k, punt) in enumerate(puntajes[:top_n], 1):
            print(f"  {rank:<4} {peliculas[k]:<30} {round(punt, 2):>10}")
        print()
# ─────────────────────main────────────────────────
def main():
    print("SISTEMA DE RECOMENDACION DE PELICULAS")

    top_n = int(input("Cuantos resultados deseas que te mostremos en cada opcion? (ej: 5 o 10): "))

    while True:
        print("Que deseas hacer?")
        print("1. Recomendaciones para un usuario por nombre: (op: Carlos,Eduardo,Lucia, etc...)")
        print("2. Recomendaciones para los primeros N usuarios de a base de datos")
        print("3. Recomendaciones para todos los usuarios")
        print("4. Encontrar usuarios similares a un usuario: (op: Carlos,Eduardo,Lucia, etc...)")
        print("5. Peliculas mas populares por genero")
        print("6. Salir")

        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            nombre = input("Ingresa el nombre del usuario: ").strip().lower()
            encontrado = False
            for i in range(len(usuarios)):
                if usuarios[i].lower() == nombre:
                    mostrar_recomendaciones(i, top_n)
                    encontrado = True
                    break
            if not encontrado:
                print("Usuario " + nombre + " no encontrado.")

        elif opcion == "2":
            cantidad = int(input("Cuantos usuarios?: "))
            if cantidad > len(usuarios):
                cantidad = len(usuarios)
            for i in range(cantidad):
                mostrar_recomendaciones(i, top_n)

        elif opcion == "3":
            for i in range(len(usuarios)):
                mostrar_recomendaciones(i, top_n)

        elif opcion == "4":
            nombre = input("Ingresa el nombre del usuario: ").strip()
            usuarios_similares(nombre, top_n)

        elif opcion == "5":
            peliculas_populares_por_genero(top_n)

        elif opcion == "6":
            print("GRACIAS")
            break

        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    main()