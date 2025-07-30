from .types import ResultTraining

class TrainingTextTemplate:
    SUCCESS_MESSAGE = "<b>Вітаю</b>! Параметр {characteristic} покращено на {points} поінта!"
    FAILURE_MESSAGE = "<b>На жаль</b>, ваш персонаж не зміг покращити {characteristic}. Спробуйте ще раз!"

    @staticmethod
    def get_training_text(result: ResultTraining, characteristic: str, points: int = 0) -> str:
        if result == ResultTraining.SUCCESS:
            return TrainingTextTemplate.SUCCESS_MESSAGE.format(characteristic=characteristic, points=points)
        return TrainingTextTemplate.FAILURE_MESSAGE.format(characteristic=characteristic)

