
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    Course,
    Question,
    Choice,
    Submission,
    Learner,
    Enrollment
)


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    learner = get_object_or_404(Learner, user=request.user)

    enrollment = get_object_or_404(
        Enrollment,
        learner=learner,
        course=course
    )

    if request.method == 'POST':
        questions = Question.objects.filter(course=course)
        selected_choices = []
        score = 0

        for question in questions:
            selected_choice_id = request.POST.get(
                f'question_{question.id}'
            )

            if selected_choice_id:
                selected_choice = get_object_or_404(
                    Choice,
                    id=selected_choice_id,
                    question=question
                )

                selected_choices.append(selected_choice)

                if selected_choice.is_correct:
                    score += question.grade

        submission = Submission.objects.create(
            user=request.user,
            course=course,
            enrollment=enrollment,
            score=score
        )

        submission.choices.set(selected_choices)

        return redirect(
            'show_exam_result',
            course_id=course.id,
            submission_id=submission.id
        )

    questions = Question.objects.filter(
        course=course
    ).prefetch_related('choices')

    return render(
        request,
        'onlinecourseapp/exam.html',
        {
            'course': course,
            'questions': questions
        }
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, id=course_id)

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        course=course,
        user=request.user
    )

    total_questions = Question.objects.filter(course=course).count()

    selected_choices = submission.choices.all()

    selected_choice_ids = list(
        selected_choices.values_list('id', flat=True)
    )

    score = sum(
        question.grade
        for question in Question.objects.filter(course=course)
        if question.is_get_score(
            selected_choices.filter(question=question).values_list(
                'id', flat=True
            )
        )
    )

    submission.score = score
    submission.save()

    return render(
        request,
        'onlinecourseapp/exam_result_bootstrap.html',
        {
            'course': course,
            'submission': submission,
            'score': score,
            'grade': score,
            'total_questions': total_questions,
            'percentage': (
                round(score / total_questions * 100)
                if total_questions else 0
            ),
            'selected_choice_ids': selected_choice_ids
        }
    )
