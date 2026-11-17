
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Question, Choice, Submission, Learner, Enrollment


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
                    score += 1

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
    score = sum(
        1 for choice in submission.choices.all()
        if choice.is_correct
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
            'total_questions': total_questions,
            'percentage': (
                round(score / total_questions * 100)
                if total_questions else 0
            )
        }
    )
