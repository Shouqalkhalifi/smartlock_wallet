from django.shortcuts import render, redirect
from .models import Lock


def add_lock(request):
    if request.method == "POST":
        lock_name = request.POST.get("name")
        room_id = request.POST.get("room_id")

        if lock_name and room_id:
            Lock.objects.create(
                name=lock_name,
                room_id=room_id,
            )
            return redirect("/locks/list/")

    return render(request, "locks/add_lock.html")
