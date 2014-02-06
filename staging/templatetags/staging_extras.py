from django import template

register = template.Library()


@register.filter(name="listsplit")
def listsplit(value, arg):
    """Get the ith split of a list into n lists."""

    print "listsplit:{0}".format(arg)
    args = arg.split(",")
    if not len(args) == 2:
        return value

    i = int(args[0])
    n = int(args[1])

    m = len(value)

    base = m // n
    rem = m % n

    sizes = [base + 1] * rem + [base] * (n - rem)

    start = sum(sizes[0:i])
    end = start + sizes[i]

    return value[start:end]

