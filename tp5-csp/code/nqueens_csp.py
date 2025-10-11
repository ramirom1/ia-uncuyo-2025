"""Solvers for the N-Queens problem formulated as a CSP.

This module provides two search strategies:
- Depth-first backtracking without look-ahead.
- Forward checking, which prunes inconsistent domain values after each assignment.

Both solvers return solutions represented as a list where the index is the column
and the value is the row in which the queen is placed.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List, Optional, Sequence, Set, Tuple

Solution = List[int]


@dataclass
class SolverMetrics:
    solutions: List[Solution]
    nodes_explored: int
    time_seconds: float

    @property
    def success(self) -> bool:
        return bool(self.solutions)

def _ensure_valid_n(n: int) -> None:
    if n < 1:
        raise ValueError("n must be a positive integer")


def _assignment_to_solution(assignment: Dict[int, int], n: int) -> Solution:
    return [assignment[col] for col in range(n)]


def _is_consistent(column: int, row: int, assignment: Dict[int, int]) -> bool:
    """Check row and diagonal conflicts with the existing assignment."""
    for other_col, other_row in assignment.items():
        if other_row == row:
            return False
        if abs(other_col - column) == abs(other_row - row):
            return False
    return True


def _ordered_rows(values: Sequence[int], rng: Optional[random.Random]) -> List[int]:
    rows = list(values)
    if rng is not None:
        rng.shuffle(rows)
    return rows


def _solve_backtracking(
    n: int, max_solutions: Optional[int], rng: Optional[random.Random]
) -> Tuple[List[Solution], int]:
    _ensure_valid_n(n)
    variables = list(range(n))
    assignment: Dict[int, int] = {}
    solutions: List[Solution] = []
    nodes_explored = 0

    def backtrack(index: int) -> bool:
        nonlocal nodes_explored
        if index == n:
            solutions.append(_assignment_to_solution(assignment, n))
            return max_solutions is not None and len(solutions) >= max_solutions

        column = variables[index]
        for row in _ordered_rows(range(n), rng):
            if not _is_consistent(column, row, assignment):
                continue
            assignment[column] = row
            nodes_explored += 1
            should_stop = backtrack(index + 1)
            del assignment[column]
            if should_stop:
                return True
        return False

    backtrack(0)
    return solutions, nodes_explored


def solve_n_queens_backtracking(
    n: int, max_solutions: Optional[int] = 1, seed: Optional[int] = None
) -> List[Solution]:
    """Solve N-Queens via plain backtracking.

    Args:
        n: Board size.
        max_solutions: Maximum number of solutions to return. Use None for all.
        seed: Optional seed that randomizes the order in which rows are explored.

    Returns:
        A list of solutions (possibly empty).
    """
    metrics = solve_n_queens_backtracking_metrics(
        n, max_solutions=max_solutions, seed=seed
    )
    return metrics.solutions


def solve_n_queens_backtracking_metrics(
    n: int, max_solutions: Optional[int] = 1, seed: Optional[int] = None
) -> SolverMetrics:
    rng = random.Random(seed) if seed is not None else None
    start = perf_counter()
    solutions, nodes = _solve_backtracking(n, max_solutions, rng)
    elapsed = perf_counter() - start
    return SolverMetrics(
        solutions=solutions, nodes_explored=nodes, time_seconds=elapsed
    )


def _apply_forward_checking(
    column: int,
    row: int,
    domains: Dict[int, Set[int]],
    assignment: Dict[int, int],
    variables: Sequence[int],
) -> Tuple[bool, Dict[int, Set[int]]]:
    """Prune inconsistent values from neighbor domains."""
    removed: Dict[int, Set[int]] = {}
    for other_col in variables:
        if other_col == column or other_col in assignment:
            continue
        current_domain = domains[other_col]
        to_remove = {
            other_row
            for other_row in current_domain
            if other_row == row or abs(other_col - column) == abs(other_row - row)
        }
        if not to_remove:
            continue
        removed[other_col] = to_remove
        current_domain.difference_update(to_remove)
        if not current_domain:
            return False, removed
    return True, removed


def _restore_domains(
    domains: Dict[int, Set[int]], removed: Dict[int, Set[int]]
) -> None:
    for column, rows in removed.items():
        domains[column].update(rows)


def solve_n_queens_forward_checking(
    n: int, max_solutions: Optional[int] = 1, seed: Optional[int] = None
) -> List[Solution]:
    """Solve N-Queens using forward checking to prune inconsistent domains."""
    metrics = solve_n_queens_forward_checking_metrics(
        n, max_solutions=max_solutions, seed=seed
    )
    return metrics.solutions


def _solve_forward_checking(
    n: int, max_solutions: Optional[int], rng: Optional[random.Random]
) -> Tuple[List[Solution], int]:
    _ensure_valid_n(n)
    variables = list(range(n))
    domains: Dict[int, Set[int]] = {col: set(range(n)) for col in variables}
    assignment: Dict[int, int] = {}
    solutions: List[Solution] = []
    nodes_explored = 0

    def search(index: int) -> bool:
        nonlocal nodes_explored
        if index == n:
            solutions.append(_assignment_to_solution(assignment, n))
            return max_solutions is not None and len(solutions) >= max_solutions

        column = variables[index]
        for row in _ordered_rows(domains[column], rng):
            if not _is_consistent(column, row, assignment):
                continue
            assignment[column] = row
            nodes_explored += 1
            success, removed = _apply_forward_checking(
                column, row, domains, assignment, variables
            )
            if success:
                should_stop = search(index + 1)
            else:
                should_stop = False
            _restore_domains(domains, removed)
            del assignment[column]
            if should_stop:
                return True
        return False

    search(0)
    return solutions, nodes_explored


def solve_n_queens_forward_checking_metrics(
    n: int, max_solutions: Optional[int] = 1, seed: Optional[int] = None
) -> SolverMetrics:
    rng = random.Random(seed) if seed is not None else None
    start = perf_counter()
    solutions, nodes = _solve_forward_checking(n, max_solutions, rng)
    elapsed = perf_counter() - start
    return SolverMetrics(
        solutions=solutions, nodes_explored=nodes, time_seconds=elapsed
    )


def format_solution(solution: Solution) -> str:
    """Format a solution as a board representation."""
    n = len(solution)
    lines = []
    for row in range(n):
        line = "".join("Q " if solution[col] == row else ". " for col in range(n))
        lines.append(line.rstrip())
    return "\n".join(lines)


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Solve the N-Queens problem using CSP techniques."
    )
    parser.add_argument("n", type=int, help="Board size (number of queens).")
    parser.add_argument(
        "--method",
        choices=("backtracking", "forward-checking"),
        default="backtracking",
        help="Search strategy to use.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Find all solutions instead of just the first one.",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Maximum number of solutions to search for (overrides --all).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for randomizing the search order (useful for experiments).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    max_solutions: Optional[int]
    if args.max is not None:
        max_solutions = args.max
    elif args.all:
        max_solutions = None
    else:
        max_solutions = 1

    if args.method == "backtracking":
        solutions = solve_n_queens_backtracking(
            args.n, max_solutions=max_solutions, seed=args.seed
        )
    else:
        solutions = solve_n_queens_forward_checking(
            args.n, max_solutions=max_solutions, seed=args.seed
        )

    if not solutions:
        print("No solutions found.")
        return 1

    for index, solution in enumerate(solutions, start=1):
        print(f"Solution #{index}")
        print(format_solution(solution))
        print()

    if max_solutions is None:
        print(f"Total solutions: {len(solutions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
