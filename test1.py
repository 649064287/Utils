def calculate_min_initial_battery(tasks_str, battery_capacity):
    tasks = tasks_str.split(',')
    task_data = []

    for task in tasks:
        power, min_initial_battery = map(int, task.split(':'))
        task_data.append((power, min_initial_battery))

    task_data.sort(key=lambda x: (x[1], x[0]))

    current_battery = 0
    min_initial = 0

    for power, min_initial_battery in task_data:
        if current_battery < min_initial_battery:
            deficit = min_initial_battery - current_battery
            min_initial += deficit
            current_battery += deficit
        current_battery -= power

    if current_battery < 0 or min_initial > battery_capacity:
        return -1
    return min_initial


# 输入任务数据和手机电池容量
tasks_str = input()
battery_capacity = 4800  # Xiaomi MIX Fold 3的大电池容量是4800mAh

result = calculate_min_initial_battery(tasks_str, battery_capacity)
print(result)