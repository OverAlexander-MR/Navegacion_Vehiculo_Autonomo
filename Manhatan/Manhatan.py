import pygame
import sys
import math
import neat
import csv
import os

# Para guaradar los datos de fitness en un archivo CSV
if (
    not os.path.exists("Manhatan/datos_fitness.csv")
    or os.path.getsize("Manhatan/datos_fitness.csv") == 0
):
    with open("Manhatan/datos_fitness.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Simulacion", "Generacion", "Mejor Fitness", "Fitness Promedio"]
        )

pygame.init()  # Inicializar Pygame antes de cualquier otra cosa

# Constantes
TRACK_COLOR = (0, 0, 0)  # Negro para la pista

class Map:
    def __init__(self, path, check_var, objetivo, check_point):
        self.image = pygame.image.load(path)
        self.width, self.height = self.image.get_size()
        self.check_var = check_var
        self.objetivo = objetivo
        self.check_pont = check_point
        self.road_positions_1 = [[1500, 687]]
        self.zoom_level = 1.0
        self.zoom_increment = 0.1
        self.offset_x, self.offset_y = 0, 0
        self.initial_pos = self.get_road_positions()

    def get_road_positions(self):
        self.lista_objetivo = []
        self.point = []
        self.lista_var = []
        for x in range(self.width):
            for y in range(self.height):
                color = self.image.get_at((x, y))[:3]
                if color == self.objetivo:
                    self.lista_objetivo.append((x, y))
                elif color == self.check_pont:
                    self.point.append((x, y))
                elif color == self.check_var:
                    self.lista_var.append((x, y))

        return True

    def zoom_in(self):
        self.zoom_level += self.zoom_increment

    def zoom_out(self):
        self.zoom_level = max(1.0, self.zoom_level - self.zoom_increment)

    def get_scaled_image(self):
        new_width = int(self.width * self.zoom_level)
        new_height = int(self.height * self.zoom_level)
        return pygame.transform.scale(self.image, (new_width, new_height))

    def update_offset(self, dx, dy):
        if self.zoom_level > 1.0:
            self.offset_x += dx
            self.offset_y += dy

    def limit_offset(self, screen_rect):
        scaled_map = self.get_scaled_image()
        scaled_map_rect = scaled_map.get_rect()
        self.offset_x = min(
            0, max(self.offset_x, screen_rect.width - scaled_map_rect.width)
        )
        self.offset_y = min(
            0, max(self.offset_y, screen_rect.height - scaled_map_rect.height)
        )


class Vehicle:
    def __init__(self, image_path, position, original_size, rotation):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.original_size = original_size
        self.position = list(position)
        self.rotation = rotation
        self.speed = 20
        self.angle = self.rotation
        self.radars = []
        self.alive = True
        self.distance = 0
        self.time = 0
        self.center = [
            self.position[0] + self.original_size[0] / 2,
            self.position[1] + self.original_size[1] / 2,
        ]
        self.time_stationary = 0
        self.max_time_stationary = 60  # Ajusta este valor según tus necesidades

        # Nuevos atributos para fitness
        self.frames_alive = 0  # Contador de frames
        # Contador de checkpoints
        self.last_checkpoint = float("inf")  # Último checkpoint alcanzado
        self.distance_penalty = 0  # Penalización por distancia
        self.check_point_bonus = 0  # Bono por checkpoint
        self.distance_reward = 0
        self.distance_reward_point = 0
        self.distance_reward_var = 0

    def update(self, game_map):
        if self.alive:
            self.frames_alive += 1
            prev_position = self.position.copy()
            # Actualizar posición basada en velocidad y ángulo
            self.position[0] += (
                math.cos(math.radians(360 - self.angle)) * self.speed
            )  # x
            self.position[1] += (
                math.sin(math.radians(360 - self.angle)) * self.speed
            )  # y

            self.distance += self.speed
            self.time += 1

            self.center = [
                int(self.position[0]) + self.original_size[0] / 2,
                int(self.position[1]) + self.original_size[1] / 2,
            ]

            # Verificar si el vehículo ha avanzado
            if self.position == prev_position:
                self.time_stationary += 1
            else:
                self.time_stationary = 0

            # Si ha estado demasiado tiempo sin avanzar, marcar como no vivo
            if self.time_stationary > self.max_time_stationary:
                self.alive = False

            # Verificar colisiones y actualizar radares
            self.check_collision(game_map)
            self.check_radars(game_map)

    def get_scaled_rotated_image(self, zoom_level):
        new_width = int(self.original_size[0] * zoom_level)
        new_height = int(self.original_size[1] * zoom_level)
        scaled_image = pygame.transform.scale(self.image, (new_width, new_height))
        return pygame.transform.rotate(scaled_image, self.angle)

    def get_scaled_position(self, zoom_level, offset_x, offset_y):
        x = int(self.position[0] * zoom_level) + offset_x
        y = int(self.position[1] * zoom_level) + offset_y
        return (x, y)

    def check_collision(self, game_map):
        self.alive = True
        for point in self.get_corners():
            if self.collides(point[0], point[1], game_map):
                self.alive = False
                break

    def get_corners(self):
        length = self.original_size[0] / 2
        width = self.original_size[1] / 2

        front_left = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]

        front_right = [
            self.center[0] + math.cos(math.radians(360 - (self.angle - 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle - 30))) * length,
        ]

        back_left = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * width,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * width,
        ]

        back_right = [
            self.center[0] + math.cos(math.radians(360 - (self.angle - 150))) * width,
            self.center[1] + math.sin(math.radians(360 - (self.angle - 150))) * width,
        ]

        return [front_left, front_right, back_left, back_right]

    def collides(self, x, y, game_map):
        if 0 <= x < game_map.width and 0 <= y < game_map.height:
            color = game_map.image.get_at((int(x), int(y)))[:3]
            # Asumiendo que las vías son negras (0, 0, 0)
            return (
                color != (0, 0, 0)
                and color != (0, 255, 0)
                and color != (0, 0, 255)
                # and color != (255, 0, 0)
            )
        else:
            return True  # Fuera de los límites es una colisión

    def check_radars(self, game_map):
        self.radars.clear()
        for degree in range(-90, 120, 45):
            self.check_radar(degree, game_map)

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0])
        y = int(self.center[1])

        while not self.collides(x, y, game_map) and length < 100:
            length += 1
            x = int(
                self.center[0]
                + math.cos(math.radians(360 - (self.angle + degree))) * length
            )
            y = int(
                self.center[1]
                + math.sin(math.radians(360 - (self.angle + degree))) * length
            )

        dist = int(math.hypot(x - self.center[0], y - self.center[1]))
        self.radars.append([degree, dist])

    def get_data(self):
        # Normalizar las distancias de los radares
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)
        return return_values

        # return [radar[1] / 300 for radar in self.radars]

    def get_reward(self):
        # Recompensa basada en la distancia recorrida
        return self.distance

    def is_alive(self):
        return self.alive

    def draw_radar(self, screen):
        for radar in self.radars:
            angle = math.radians(360 - (self.angle + radar[0]))
            x = int(self.center[0] + math.cos(angle) * radar[1])
            y = int(self.center[1] + math.sin(angle) * radar[1])
            pygame.draw.line(screen, (0, 255, 0), self.center, (x, y), 1)
            pygame.draw.circle(screen, (0, 255, 0), (x, y), 2)

    def calculate_fitness(self):
        distance_to_goal = self.calculate_manhattan_distance(self.map.lista_objetivo[0])
        fitness = max(
            0, 10000 - distance_to_goal
        )  # Ajusta el valor base según sea necesario
        return fitness

    def calculate_manhattan_distance(self, target_position):
        dx = abs(self.center[0] - target_position[0])
        dy = abs(self.center[1] - target_position[1])
        return dx + dy


class Game:
    def __init__(self):
        pygame.init()
        self.map = Map("Maps/gta.png", (255, 0, 0), (0, 255, 0), (0, 0, 255))
        self.screen = pygame.display.set_mode((self.map.width, self.map.height))
        pygame.display.set_caption("Simulación de Carro Autónomo")
        self.clock = pygame.time.Clock()
        self.running = True
        self.x = (0, 0)
        self.simulacion_num = self.obtener_numero_simulacion()
        self.generacion_actual = 0

    def run(self):
        config_path = "neat_config/cop.txt"
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path,
        )
        self.run_neat(config)

    def run_neat(self, config):
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        winner = population.run(self.eval_genomes, 50)

        # Al finalizar, generar las gráficas
        self.plot_statistics(stats)

    def plot_statistics(self, stats):
        import os
        import csv

        if len(stats.most_fit_genomes) == 0:
            print("No hay datos de fitness en 'stats'.")
            return

        generation = range(len(stats.most_fit_genomes))
        best_fitness = [genome.fitness for genome in stats.most_fit_genomes]
        avg_fitness = stats.get_fitness_mean()

        with open("Manhatan/datos_fitness.csv", mode="a", newline="") as file:
            writer = csv.writer(file)

            if os.path.getsize("Manhatan/datos_fitness.csv") == 0:
                writer.writerow(
                    ["Simulacion", "Generacion", "Mejor Fitness", "Fitness Promedio"]
                )

            for gen, best, avg in zip(generation, best_fitness, avg_fitness):
                writer.writerow([self.simulacion_num, gen, best, avg])

    def obtener_numero_simulacion(self):
        try:
            with open("Manhatan/contador_simulaciones.txt", "r") as f:
                contador = int(f.read().strip())
        except (FileNotFoundError, ValueError):
            contador = 0

        contador += 1

        with open("Manhatan/contador_simulaciones.txt", "w") as f:
            f.write(str(contador))

        return contador

    def eval_genomes(self, genomes, config):
        import csv  # Asegúrate de importar csv

        self.generacion_actual += 1  # Incrementar la generación actual
        nets = []
        cars = []
        ge = []
        genome_ids = []
        fitness_individual = []

        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            position = self.map.road_positions_1[0]
            car = Vehicle("Cars/f1.png", position, (30, 20), 90)
            car.map = self.map
            cars.append(car)

            genome.fitness = 0
            ge.append(genome)
            genome_ids.append(genome_id)

        while self.running and len(cars) > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        pygame.quit()
                        sys.exit()

            for i in range(len(cars) - 1, -1, -1):
                car = cars[i]
                if car.alive:
                    prev_pos = car.position.copy()
                    car.update(self.map)
                    movement = math.hypot(
                        car.position[0] - prev_pos[0], car.position[1] - prev_pos[1]
                    )

                    if movement < 0.01:
                        car.time_stationary += 1
                        if car.calculate_fitness() < ge[i].fitness:
                            car.alive = False
                    else:
                        car.time_stationary = 0

                    if car.time_stationary > car.max_time_stationary:
                        # Guardar el fitness antes de eliminar
                        ge[i].fitness = car.calculate_fitness()
                        fitness_individual.append(
                            {
                                "simulacion": self.simulacion_num,
                                "generacion": self.generacion_actual,
                                "genome_id": genome_ids[i],
                                "fitness": ge[i].fitness,
                            }
                        )
                        cars.pop(i)
                        nets.pop(i)
                        ge.pop(i)
                        genome_ids.pop(i)
                        continue

                    output = nets[i].activate(car.get_data())
                    car.angle += (output[0] - 0.5) * 10
                    car.speed = max(0, min(5, output[1] * 5))
                    ge[i].fitness = car.calculate_fitness()

                    # Refuerzo Forzado o Metodo de Aceleracion	
                    if car.speed < 0.1:
                        car.angle += (output[0] - 0.5) * 10
                        car.speed = 5

                else:
                    # Guardar el fitness antes de eliminar
                    ge[i].fitness = car.calculate_fitness()
                    fitness_individual.append(
                        {
                            "simulacion": self.simulacion_num,
                            "generacion": self.generacion_actual,
                            "genome_id": genome_ids[i],
                            "fitness": ge[i].fitness,
                        }
                    )
                    cars.pop(i)
                    nets.pop(i)
                    ge.pop(i)
                    genome_ids.pop(i)

            self.render_simulation(cars)
            self.clock.tick(60)

        # Al finalizar la generación, guarda los fitness de los genomas que aún estén vivos
        for i in range(len(cars) - 1, -1, -1):
            ge[i].fitness = car.calculate_fitness()
            fitness_individual.append(
                {
                    "simulacion": self.simulacion_num,
                    "generacion": self.generacion_actual,
                    "genome_id": genome_ids[i],
                    "fitness": ge[i].fitness,
                }
            )
            cars.pop(i)
            nets.pop(i)
            ge.pop(i)
            genome_ids.pop(i)

        # Guardar los fitness individuales en un archivo CSV
        with open("Manhatan/fitness_individual.csv", mode="a", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=["simulacion", "generacion", "genome_id", "fitness"]
            )
            # Escribir encabezados si el archivo está vacío
            if file.tell() == 0:
                writer.writeheader()
            # Escribir los datos
            for dato in fitness_individual:
                writer.writerow(dato)

    def render_simulation(self, cars):
        self.screen.fill((255, 255, 255))
        scaled_map = self.map.get_scaled_image()
        self.screen.blit(scaled_map, (self.map.offset_x, self.map.offset_y))
        for car in cars:
            if car.alive:
                scaled_vehicle_image = car.get_scaled_rotated_image(self.map.zoom_level)
                scaled_position = car.get_scaled_position(
                    self.map.zoom_level, self.map.offset_x, self.map.offset_y
                )
                self.screen.blit(scaled_vehicle_image, scaled_position)
                # Dibujar radares para depuración
                car.draw_radar(self.screen)
        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
