from utils import enumerate_resume, make_printv, write_jsonl, resume_success_count
from executors import executor_factory
from generators import generator_factory, model_factory
from typing import List
import os


def run_reflexion(
    dataset: List[dict],
    model_name: str,
    language: str,
    max_iters: int,
    pass_at_k: int,
    log_path: str,
    verbose: bool,
    is_leetcode: bool = False
) -> None:
    exe = executor_factory(language, is_leet=is_leetcode)
    gen = generator_factory(language)
    model = model_factory(model_name)
    print_v = make_printv(verbose)

    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    num_items = len(dataset)
    num_success = resume_success_count(dataset)

    print_v(f"🔁 Starting Reflexion loop for {num_items} problems...")

    for i, item in enumerate_resume(dataset, log_path):
        cur_pass = 0
        is_solved = False
        reflections = []
        implementations = []
        test_feedback = []
        cur_func_impl = ""

        # Per-problem logging object
        problem_log = {
            "name": item.get("name", f"Problem_{i}"),
            "prompt": item.get("prompt", ""),
            "language": language,
            "model": model_name,
            "iterations": []
        }

        while cur_pass < pass_at_k and not is_solved:
            if is_leetcode:
                tests_i = item["visible_tests"]
            else:
                tests_i = gen.internal_tests(item["prompt"], model, 1)

            # 1️⃣ Initial attempt
            cur_func_impl = gen.func_impl(item["prompt"], model, "simple")

            if not isinstance(cur_func_impl, str) or not cur_func_impl.strip():
                print_v(f"⚠️ Empty model output on {item.get('name', i)}, skipping...")
                problem_log["iterations"].append({
                    "iteration": 0,
                    "error": "Empty or invalid model output"
                })
                write_jsonl(log_path, [problem_log], append=True)
                break

            implementations.append(cur_func_impl)
            is_passing, feedback, _ = exe.execute(cur_func_impl, tests_i)
            test_feedback.append(feedback)

            # Log iteration 0
            problem_log["iterations"].append({
                "iteration": 0,
                "func_impl": cur_func_impl,
                "feedback": feedback,
                "is_passing": is_passing
            })

            # 2️⃣ If passes all tests → stop early
            if is_passing:
                is_passing = exe.evaluate(
                    item["entry_point"], cur_func_impl, item["test"], timeout=10
                )
                is_solved = is_passing
                num_success += int(is_passing)
                problem_log["final_solution"] = cur_func_impl
                break

            # 3️⃣ Reflexion iterations
            cur_iter = 1
            cur_feedback = feedback
            while cur_iter < max_iters:
                reflection = gen.self_reflection(cur_func_impl, cur_feedback, model)
                reflections.append(reflection)

                cur_func_impl = gen.func_impl(
                    func_sig=item["prompt"],
                    model=model,
                    strategy="reflexion",
                    prev_func_impl=cur_func_impl,
                    feedback=cur_feedback,
                    self_reflection=reflection,
                )

                if not isinstance(cur_func_impl, str) or not cur_func_impl.strip():
                    print_v(f"⚠️ Empty model output at iter {cur_iter}, skipping.")
                    problem_log["iterations"].append({
                        "iteration": cur_iter,
                        "error": "Empty model output"
                    })
                    break

                implementations.append(cur_func_impl)
                is_passing, cur_feedback, _ = exe.execute(cur_func_impl, tests_i)
                test_feedback.append(cur_feedback)

                problem_log["iterations"].append({
                    "iteration": cur_iter,
                    "reflection": reflection,
                    "func_impl": cur_func_impl,
                    "feedback": cur_feedback,
                    "is_passing": is_passing
                })

                # 4️⃣ Final test check
                if is_passing or cur_iter == max_iters - 1:
                    is_passing = exe.evaluate(
                        item["entry_point"], cur_func_impl, item["test"], timeout=10
                    )
                    if is_passing:
                        item["solution"] = cur_func_impl
                        is_solved = True
                        num_success += 1
                        problem_log["final_solution"] = cur_func_impl
                    break

                cur_iter += 1

            cur_pass += 1

        # Save everything for this problem
        item["is_solved"] = is_solved
        item["reflections"] = reflections
        item["implementations"] = implementations
        item["test_feedback"] = test_feedback
        item["solution"] = cur_func_impl

        problem_log["is_solved"] = is_solved
        problem_log["accuracy"] = round(num_success / (i + 1), 3)

        write_jsonl(log_path, [problem_log], append=True)
        print_v(f"✅ completed {i+1}/{num_items}: acc = {round(num_success/(i+1), 2)}")