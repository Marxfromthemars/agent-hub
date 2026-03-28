"""
3 AGENTS SOLVE A PROBLEM
- Planner breaks problem into tasks
- Executor does work
- Reviewer validates result
"""
import json
import requests

BASE = "http://localhost"

def solve_problem(problem_title):
    print(f"\nSolving: {problem_title}")
    
    # 1. Create task
    r = requests.post(f"{BASE}:8302/tasks/create", json={"title": problem_title, "creator": "system"})
    task = r.json()["task"]
    task_id = task["id"]
    print(f"  Task created: #{task_id}")
    
    # 2. Planner breaks it down
    r = requests.post(f"{BASE}:8304/agent/cycle", json={"agent": "planner"})
    plan = r.json()
    print(f"  Planner: {plan['thought']}")
    
    # 3. Executor does work
    r = requests.post(f"{BASE}:8302/tasks/assign", json={"task_id": task_id, "agent": "executor"})
    r = requests.post(f"{BASE}:8302/tasks/execute", json={"task_id": task_id, "agent": "executor"})
    result = r.json()
    print(f"  Executor: {result.get('result', result)}")
    
    # 4. Reviewer validates
    r = requests.post(f"{BASE}:8302/tasks/review", json={"task_id": task_id, "reviewer": "reviewer", "quality": 80})
    review = r.json()
    print(f"  Review: quality={review.get('quality')}, status={review.get('status')}")
    
    return review

# Test with 3 problems
print("=" * 50)
print("3 AGENTS SOLVING PROBLEMS")
print("=" * 50)

solve_problem("Calculate 2+2")
solve_problem("Reverse string 'hello'")
solve_problem("Find max in [1,5,3]")