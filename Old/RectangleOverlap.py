def overlapBetweenRectangles(bbox1, bbox2):
    left1, right1, up1, down1 = bbox1
    left2, right2, up2, down2 = bbox2

    left            = max(left1, left2)
    right           = min(right1, right2) 
    overlapWidth    = right - left
    
    down            = min(down1, down2)  
    up              = max(up1, up2)
    overlapHeight   = down - up

    if overlapWidth>0 and overlapHeight>0:
        return [left, right, up, down], overlapWidth*overlapHeight
    else:
        return -1, -1


b1 = [10, 20, 10, 20]
b2 = [19, 25, 15, 25]


    
print overlapBetweenRectangles(b1, b2)
