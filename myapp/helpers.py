import math
import random
from typing import List, Tuple, Set


class TabuSearch:
    def __init__(self, dm):
        self.dm = dm

    def search(
        self,
        soln_init: list[int],
    ) -> tuple[int, list[int], int]:
        iter_max = 500

        tabu_list: list[tuple[int, int]] = []
        soln_curr: list[int] = soln_init
        soln_best: list[int] = soln_init
        soln_best_tracker: list[int] = []

        stagnant_ctr: int = 0
        stagnant_best: int = 0

        tabu_tenure: int = math.floor(len(soln_init) * 0.1)
        improvement_rate: float = 0.0
        solution_diversity_tracker: list[list[int]] = []

        for iter_ctr in range(iter_max):

            solution_diversity_tracker.append(soln_curr)
            solution_diversity = len(set(map(tuple, solution_diversity_tracker))) / len(
                solution_diversity_tracker
            )

            if len(soln_best_tracker) > 1:
                improvement_rate = abs(
                    (soln_best_tracker[-1] - soln_best_tracker[-2])
                    / (soln_best_tracker[-1] + 1e-10)
                )

            tabu_tenure = self.quantum_tenure_adaptation(
                soln_init,
                tabu_tenure,
                iter_ctr,
                iter_max,
                solution_diversity,
                improvement_rate,
            )

            if stagnant_ctr:
                soln_curr = self.wave_resonance_perturbation(
                    soln_curr, iter_ctr, iter_max, soln_best, stagnant_ctr
                )

            nbhd, moves = self.neighborhood(soln_curr, tabu_list)

            nbhr_best, move_best = self.best_admissible_soln(
                nbhd, moves, tabu_list, soln_best
            )

            if self.val(nbhr_best) < self.val(soln_best):
                soln_best = nbhr_best
                soln_best_tracker.append(self.val(soln_best))

                if stagnant_ctr > stagnant_best:
                    stagnant_best = stagnant_ctr

                stagnant_ctr = 0
            else:
                stagnant_ctr += 1

            soln_curr = nbhr_best.copy()

            while len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)
            tabu_list.append(move_best)

        soln_best.append(soln_best[0])

        return soln_best

    def neighborhood(
        self, soln: list[int], tabu_list: list[tuple[int, int]]
    ) -> tuple[list[list[int]], list[tuple[int, int]]]:
        nbhd = []
        moves = []
        n = len(soln) - 1

        segment_costs = []
        for i in range(n):
            next_idx = i + 1
            cost = self.dm[soln[i]][soln[next_idx]]
            segment_costs.append((i, cost))

        segment_costs.sort(key=lambda x: x[1], reverse=True)

        k = max(2, int(n**0.3))
        focal_indices = [p[0] for p in segment_costs[:k]]

        non_focal = [i for i in range(n) if i not in focal_indices]
        if non_focal:
            random_idx = random.choice(non_focal)
            if random_idx not in focal_indices:
                focal_indices.append(random_idx)

        for i in focal_indices:
            radius = max(2, int(2 * n))

            j_candidates = set()

            for offset in range(1, min(radius + 1, n)):
                j_candidates.add((i + offset) % n)
                j_candidates.add((i - offset + n) % n)

            for focal in focal_indices:
                if focal != i:
                    j_candidates.add(focal)

            for j in [j for j in j_candidates if j > i and j < n]:
                soln_mod = soln.copy()
                soln_mod[i], soln_mod[j] = soln_mod[j], soln_mod[i]

                if (soln[i], soln[j]) in tabu_list:
                    continue

                nbhd.append(soln_mod)
                moves.append((soln[i], soln[j]))

        return nbhd, moves

    def wave_resonance_perturbation(
        self,
        soln_curr: list[int],
        iter_ctr: int,
        iter_max: int,
        soln_best: list[int],
        stagnant_ctr: int,
    ) -> list[int]:
        n = len(soln_curr)

        progress_metrics = {
            "iter_progress": iter_ctr / iter_max,
            "stagnation_factor": min(1, stagnant_ctr / iter_max),
            "scale_factor": 0.5 + (n // 50),
        }

        perturbation_intensity = (
            progress_metrics["iter_progress"] + progress_metrics["stagnation_factor"]
        ) * progress_metrics["scale_factor"]

        wave_amplitude = max(
            1,
            int(
                n
                * (1 - perturbation_intensity)
                * (1 + stagnant_ctr / iter_max)
                * (1 + math.log(n) / 10)
            ),
        )

        resonance_factor = math.sin(
            perturbation_intensity * math.pi * 2 * (1 + math.log(n) / 10)
        )

        perturbed_soln = soln_curr.copy()

        for _ in range(wave_amplitude):
            wave_centers = [
                int(
                    n
                    * abs(
                        math.sin(
                            i
                            * resonance_factor
                            * (1 + stagnant_ctr / iter_max)
                            * (1 + math.log(n) / 10)
                        )
                    )
                )
                for i in range(wave_amplitude)
            ]

            for center in wave_centers:
                wave_radius = max(
                    1,
                    int(
                        wave_amplitude
                        * (1 - abs(resonance_factor))
                        * (1 + stagnant_ctr / iter_max)
                        * (1 + math.log(n) / 10)
                    ),
                )

                swap_candidates = set()
                for offset in range(-wave_radius, wave_radius + 1):
                    candidate = (center + offset) % n
                    swap_candidates.add(candidate)

                if len(swap_candidates) > 1:
                    swap_point1, swap_point2 = random.sample(list(swap_candidates), 2)

                    swap_probability = max(
                        0.3, 1 - self.val(perturbed_soln) / self.val(soln_best)
                    )

                    if random.random() < swap_probability:
                        if self.val(perturbed_soln) < self.val(soln_best):
                            perturbed_soln[swap_point1], perturbed_soln[swap_point2] = (
                                perturbed_soln[swap_point2],
                                perturbed_soln[swap_point1],
                            )

        return perturbed_soln

    def quantum_tenure_adaptation(
        self,
        soln_init: list[int],
        base_tenure: int,
        iter_ctr: int,
        iter_max: int,
        solution_diversity: float,
        improvement_rate: float,
    ) -> int:
        quantum_wave = math.sin(2 * math.pi * iter_ctr / iter_max)

        entanglement_factor = (
            solution_diversity * (1 + improvement_rate) * abs(quantum_wave)
        )

        dynamic_tenure = int(
            base_tenure * (1 + entanglement_factor * (1 - abs(quantum_wave)))
        )

        return max(
            min(dynamic_tenure, len(soln_init) * 2), max(3, int(len(soln_init) * 0.1))
        )

    def val(self, solution: list[int]) -> int:
        total_distance = 0
        n = len(solution)

        for i in range(n):
            poi_first: int = solution[i]
            poi_second: int = solution[(i + 1) % n]
            total_distance += self.dm[poi_first][poi_second]

        return total_distance

    def best_admissible_soln(
        self,
        neighborhood: list[list[int]],
        moves: list[tuple[int, int]],
        tabu_list: list[tuple[int, int]],
        soln_best: list[int],
    ) -> tuple[list[int], tuple[int, int]]:

        best_val = float("inf")
        best_idx = 0

        for i, nbr in enumerate(neighborhood):
            nbr_val = self.val(nbr)
            if nbr_val < best_val and (
                moves[i] not in tabu_list or nbr_val < self.val(soln_best)
            ):
                best_val = nbr_val
                best_idx = i

        return neighborhood[best_idx], moves[best_idx]
