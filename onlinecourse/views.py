from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, Question, Choice, Submission

def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course})

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    # Get or create an enrollment record for testing
    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)

    if request.method == 'POST':
        selected_choice_ids = [
            int(value) for key, value in request.POST.items() if key.startswith('choice_')
        ]
        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.set(selected_choice_ids)
        submission.save()

        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = submission.choices.values_list('id', flat=True)

    total_score = 0
    total_possible = 0

    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            total_possible += question.grade
            if question.is_get_score(selected_ids):
                total_score += question.grade

    grade = (total_score / total_possible * 100) if total_possible > 0 else 0

    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'grade': grade,
        'total_score': total_score,
        'total_possible': total_possible,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)