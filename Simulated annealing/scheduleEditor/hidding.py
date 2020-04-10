def hide_widget(wid, dohide=True):
    if hasattr(wid, 'saved_hide_attrs'):
        if not dohide:
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x = wid.saved_hide_attrs
            del wid.saved_hide_attrs
    elif dohide:
        wid.saved_hide_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x = 0, None, 0, True, 0, None

def setHiddenAttr(wid, attrName, value):
    if hasattr(wid, 'saved_hide_attrs'):
        height, size_hint_y, opacity, disabled, width, size_hint_x = wid.saved_hide_attrs
        if attrName == 'height':
            height = value
        elif attrName == 'size_hint_y':
            size_hint_y = value
        elif attrName == 'opacity':
            opacity = value
        elif attrName == 'disabled':
            disabled = value
        elif attrName == 'width':
            width = value
        elif attrName == 'size_hint_x':
            size_hint_x = value
        else:
            setattr(wid, attrName, value)
        wid.saved_hide_attrs = height, size_hint_y, opacity, disabled, width, size_hint_x
    else:
        setattr(wid, attrName, value)

def getHiddenAttr(wid, attrName):
    if hasattr(wid, 'saved_hide_attrs'):
        height, size_hint_y, opacity, disabled, width, size_hint_x = wid.saved_hide_attrs
        if attrName == 'height':
            return height
        elif attrName == 'size_hint_y':
            return size_hint_y
        elif attrName == 'opacity':
            return opacity
        elif attrName == 'disabled':
            return disabled
        elif attrName == 'width':
            return width
        elif attrName == 'size_hint_x':
            return size_hint_x
        else:
            return getattr(wid, attrName)
    else:
        return getattr(wid, attrName)