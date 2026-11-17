
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Question, Choice, Submission


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        questions = Question.objects.filter(course=course)
        score = 0

        for question in questions:
            selected_choice_id = request.POST.get(
                f'question_{question.id}'
            )

            if selected_choice_id:
                selected_choice = Choice.objects.filter(
                    id=selected_choice_id,
                    question=question
                ).first()

                if selected_choice and selected_choice.is_correct:
                    score += 1

        submission = Submission.objects.create(
            user=request.user,
            course=course,
            score=score
        )

        return redirect(
            'show_exam_result',
            submission_id=submission.id
        )

    questions = Question.objects.filter(
        course=course
    ).prefetch_related('choices')

    return render(request, 'onlinecourseapp/exam.html', {
        'course': course,
        'questions': questions
    })


@login_required
def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )

    return render(request, 'onlinecourseapp/exam_result_bootstrap.html', {
        'submission': submission,
        'course': submission.course,
        'score': submission.score
    })
