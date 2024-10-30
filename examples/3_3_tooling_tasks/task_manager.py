from cel.assistants.state_manager import AsyncStateManager


class TaskManager:
    def __init__(self, state_mngr: AsyncStateManager):
        self.state_mngr = state_mngr

    async def add_task(self, task):
        async with self.state_mngr as state:
            tasks = state.get("tasks", [])
            assert isinstance(tasks, list), "Tasks must be a list"
            tasks.append(task)
            state["tasks"] = tasks

    async def get_tasks(self):
        async with self.state_mngr as state:
            return state.get("tasks", [])
        
    async def clear_tasks(self):
        async with self.state_mngr as state:
            state["tasks"] = []
            
    async def remove_task(self, task):
        async with self.state_mngr as state:
            tasks = state.get("tasks", [])
            assert isinstance(tasks, list), "Tasks must be a list"
            tasks.remove(task)
            state["tasks"] = tasks