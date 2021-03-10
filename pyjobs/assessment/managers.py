from django.db import models


class AssessmentQuerySet(models.QuerySet):
    def assessment_grade(self, user, assessment):
        all_answers = self.filter(
            user=user,
            question__assessment=assessment,
        )
        correct_answers = all_answers.filter(correct_answer=True).count()
        total_answers = all_answers.count()

        return correct_answers / total_answers

    def unanswered_questions(self, user, assessment):
        """
        Retrieves if the test has already been initiated
        and if the user needs to answer any other question
        """
        all_answers = self.filter(
            user=user,
        ).count()

        if assessment.question_count == all_answers:
            return True, True

        if (all_answers > 0) and (all_answers < assessment.question_count):
            return True, False

        return False, False
