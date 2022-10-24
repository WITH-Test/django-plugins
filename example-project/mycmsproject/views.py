from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render


def index(request):
    return render(request, "index.html")


def content_list(request, plugin):
    from .models import Content
    from .plugins import ContentType

    ct = ContentType.get_plugin(plugin)
    posts = Content.objects.filter(plugin__name=plugin)

    return render(
        request,
        "content/list.html",
        {
            "plugin": ct,
            "posts": posts,
        },
    )


def content_create(request, plugin):
    # Break circular import
    from .forms import ContentForm
    from .plugins import ContentType

    plugin = ContentType.get_plugin(plugin)
    if request.method == "POST":
        form = ContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.plugin = plugin.get_model()
            content.save()
            return HttpResponseRedirect(content.get_absolute_url())
        else:
            return "[ERROR] from views: {0}".format(form.errors)
    else:
        form = ContentForm()
    return render(
        request,
        "content/form.html",
        {
            "form": form,
        },
    )


def content_read(request, pk, plugin):
    from .models import Content
    from .plugins import ContentType

    plugin = ContentType.get_plugin(plugin)
    content = get_object_or_404(Content, pk=pk, plugin=plugin.get_model())
    return render(
        request,
        "content/read.html",
        {
            "plugin": plugin,
            "content": content,
        },
    )
