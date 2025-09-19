from .entities import Pipeline
from .repository import PipelineRepository


class PipelineService:
    """Бизнес-логика для работы с пайплайнами"""

    def __init__(self, repo: PipelineRepository):
        self.repo = repo

    async def create_pipeline(self, pipeline: Pipeline) -> Pipeline:
        # тут можно делать доменные проверки
        await self.repo.add(pipeline)
        return pipeline

    async def run_pipeline(self, pipeline_id: str, user_input: str) -> str:
        pipeline = await self.repo.get(pipeline_id)
        # здесь логика запуска агентов (пока можно сделать заглушку)
        return f"Pipeline {pipeline.name} получил ввод: {user_input}"
