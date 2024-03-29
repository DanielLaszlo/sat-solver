from problem import Problem
from metrics import Metrics
from simplification import simplify


def solve_problem(parsed_dimacs, heuristic, biased_coin, verbose=False):

    problem = Problem(parsed_dimacs)
    assignments = problem.initialise_assignments_from_rules()

    metrics = Metrics()

    return solve_sub_problem(
        problem=problem,
        assignments=assignments,
        metrics=metrics,
        heuristic=heuristic,
        biased_coin=biased_coin,
        verbose=verbose,
    )


def solve_sub_problem(
    problem, assignments, metrics, heuristic, biased_coin=False, verbose=False
):
    with problem.checkpoint():
        with assignments.checkpoint():
            problem, assignments = simplify(
                problem, assignments, metrics, verbose=verbose
            )

            if assignments.is_all_assigned():
                if problem.satisfied(assignments):
                    assignments.set_solved()
                    return True, assignments
                else:
                    metrics.backtrack()
                    return False, None

            if not problem.still_satisfiable(assignments):
                metrics.backtrack()
                return False, None
            else:
                with assignments.printing(verbose):

                    variable_name, first_assignment = assignments.pick_variable(
                        problem, heuristic, biased_coin=biased_coin
                    )

                    assignments[variable_name] = first_assignment
                    metrics.pick_var()

                    result = solve_sub_problem(
                        problem,
                        assignments,
                        metrics,
                        heuristic,
                        biased_coin,
                        verbose=verbose,
                    )

                    if result[0]:
                        return result

                    opposite = not assignments[variable_name]
                    assignments[variable_name] = None
                    assignments[variable_name] = opposite
                    metrics.flip()

                    result = solve_sub_problem(
                        problem,
                        assignments,
                        metrics,
                        heuristic,
                        biased_coin,
                        verbose=verbose,
                    )

                    if result[0]:
                        return result
                    else:
                        metrics.backtrack()
                        return False, None
