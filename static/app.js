document.addEventListener('DOMContentLoaded', fetchTasks);

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        const taskDetails = document.createElement('span');
        const priority = task.priority || 'Medium';
        const priorityBadge = document.createElement('span');
        const prioritySelect = createPrioritySelect(priority);
        const updateButton = document.createElement('button');
        const deleteButton = document.createElement('button');

        taskDetails.className = 'task-details';
        taskDetails.textContent = task.title;
        priorityBadge.className = `priority priority-${priority.toLowerCase()}`;
        priorityBadge.textContent = priority;
        prioritySelect.addEventListener('change', () => {
            priorityBadge.textContent = prioritySelect.value;
            priorityBadge.className =
                `priority priority-${prioritySelect.value.toLowerCase()}`;
        });

        updateButton.className = 'update-btn';
        updateButton.textContent = 'Update';
        updateButton.addEventListener('click', () => {
            updateTask(task.id, prioritySelect.value);
        });

        deleteButton.className = 'delete-btn';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        taskDetails.appendChild(priorityBadge);
        li.appendChild(taskDetails);
        li.appendChild(prioritySelect);
        li.appendChild(updateButton);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}

function createPrioritySelect(priority) {
    const select = document.createElement('select');
    select.className = 'task-priority-editor';
    select.setAttribute('aria-label', 'Edit task priority');

    ['Low', 'Medium', 'High'].forEach(optionValue => {
        const option = document.createElement('option');
        option.value = optionValue;
        option.textContent = optionValue;
        option.selected = optionValue === priority;
        select.appendChild(option);
    });

    return select;
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();
    const priority = priorityInput.value || 'Medium';

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    titleInput.value = '';
    priorityInput.value = 'Medium';
    fetchTasks();
}

async function updateTask(id, priority) {
    const selectedPriority = priority || 'Medium';

    await fetch(`/api/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priority: selectedPriority })
    });

    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
