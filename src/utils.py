def get_beginning_of_modulo_location(arr, modulo):
    """Returns the location of the first element in the latest sequence that is equal or shorter than the modulo value
    Example: if len(arr)==16 and modulo==7, this method will return 14"""
    l = len(arr)
    mod = l % modulo
    if mod == 0:
        mod = modulo
    return len(arr) - mod
