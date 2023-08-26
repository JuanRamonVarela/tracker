from django import template

register=template.Library()
# declare variable to contain filters
filters=''

# declare simpletag to get filters in template
@register.simple_tag
def searchFilter():
    return filters

# concat the filters from for loop
@register.simple_tag
def update_variable(filter, name):
    """Allows to update existing variable in template"""
    concat=str(filter)+str(name)
    global filters
    # print(filters.find(concat))
    if filters.find(concat)==-1:
        filters+=concat
    

    return concat