import time

#I'm inspired by the dashing library, but I can't get the most recent version

fill_chars=[" ","░","▒","▓","█"]
def map_val_to_fill(val):
    if val>=1:
        return "█"
    if val<=0:
        return " "
    return fill_chars[int(val*len(fill_chars))]
vblock_chars=[" ","▁","▂","▃","▄","▅","▆","▇","█"]
def map_val_to_vblock(val):
    if val>=1:
        return "█"
    if val<=0:
        return " "
    return vblock_chars[int(val*len(vblock_chars))]

class ScreenTile:
    def __init__(self,rect=(0,0,0,0)):
        self.rect=rect

    def draw(self,term):
        ...

    def resized(self):
        ...

class VStackTile(ScreenTile):
    def __init__(self,rect=(0,0,0,0),tiles=[]):
        super().__init__(rect)
        self.tiles=tiles
        self.adjust_tiles()

    def adjust_tiles(self):
        y_pos=0
        for tile in self.tiles:
            tile.rect=(self.rect[0],self.rect[1]+y_pos,self.rect[2],tile.rect[3])
            y_pos+=tile.rect[3]+1
            tile.resized()

    def resized(self):
        self.adjust_tiles()
        return super().resized()

    def draw(self,term):
        for t in self.tiles:
            t.draw(term)

    def append(self,tile):
        self.tiles.append(tile)

class HStackTile(ScreenTile):
    def __init__(self,rect=(0,0,0,0),tiles=[]):
        super().__init__(rect)
        self.tiles=tiles
        self.adjust_tiles()

    def adjust_tiles(self):
        x_pos=0
        for tile in self.tiles:
            tile.rect=(self.rect[0]+x_pos,self.rect[1],tile.rect[2],self.rect[3])
            x_pos+=tile.rect[2]
            tile.resized()

    
    def resized(self):
        self.adjust_tiles()
        return super().resized()

    def draw(self,term):
        for t in self.tiles:
            t.draw(term)

    def append(self,tile):
        self.tiles.append(tile)
        self.ajust_tiles()

class BorderedTile(ScreenTile):
    def __init__(self,rect=(0,0,0,0),title=None):
        super().__init__(rect)
        self.border_dirty=True
        self.title=title

    def draw_border(self,term):
        top_border="┌"+"─"*(self.rect[2]-2)+"┐"
        if self.title:
            border_array=list(top_border)
            title_start=(self.rect[2]-len(self.title))//2
            for i in range(0,len(self.title)):
                border_array[i+title_start]=self.title[i]
            top_border="".join(border_array)
        bottom_border="└"+"─"*(self.rect[2]-2)+"┘"
        edge="│"+" "*(self.rect[2]-2)+"│"
        print(term.move_xy(self.rect[0],self.rect[1])+top_border,end=" ",flush=True)
        print(term.move_xy(self.rect[0],self.rect[1]+self.rect[3])+bottom_border,end=" ",flush=True)
        for i in range(1,self.rect[3]):
            print(term.move_xy(self.rect[0],self.rect[1]+i)+edge,end=" ",flush=True)

    def draw(self,term):
        if self.border_dirty:
            self.draw_border(term)
            self.border_dirty=False
        

class TextTile(BorderedTile):
    def __init__(self,text,rect=(0,0,0,0),title=None):
        super().__init__(rect,title)
        self.text=text

    def draw(self,term):
        super().draw(term)
        textline=" "*(self.rect[2]-2)
        textline_array=list(textline)
        text_start=(self.rect[2]-2-len(self.text))//2
        for i in range(0,len(self.text)):
            textline_array[i+text_start]=self.text[i]
        textline="".join(textline_array)
        center_y=self.rect[1]+(self.rect[3]+1)//2
        print(term.move_xy(self.rect[0]+1,center_y)+textline,end="",flush=True)

class ValueTile(TextTile):
    def __init__(self,value,rect=(0,0,0,0),title=None,units=""):
        super().__init__("",rect,title)
        self.units=units
        self.set_value(value)

    def set_value(self,value):
        self.text="{:.2f} {}".format(value,self.units)

class TextEntryTile(TextTile):
    def __init__(self,text,rect=(0,0,0,0),title=None):
        super().__init__(text,rect,title)

    def draw(self,term):
        super().draw(term)
        #center_x=self.rect[0]+(self.rect[2]-len(self.text))//2
        #center_y=self.rect[1]+(self.rect[3]+1)//2
        #print(term.move_xy(center_x+self.cursor_position,center_y)+"_",end=" ",flush=True)

    def handle_key(self,key):
        if key.name=="KEY_BACKSPACE":
            self.text=self.text[:-1]
        elif not key.is_sequence:
            self.text+=key

class TwoWayHGauge(BorderedTile):
    def __init__(self,rect=(0,0,0,0),bounds=(-1,1),title=""):
        super().__init__(rect,title=title)
        self.rect=rect
        self.bounds=bounds
        self.units="V"
        self.set_value(0)
        self.content_dirty=True

    def get_bounds_center(self):
        return 0.5*(self.bounds[1]+self.bounds[0])
    
    def set_value(self,v):
        self.value=v
        self.content_dirty=True

    def draw(self,term):
        super().draw(term)
        if not self.content_dirty:
            return
        x=(self.value-self.get_bounds_center())/(self.bounds[1]-self.bounds[0])
        scaled_x=(self.rect[2]-2)*x
        bar_text=" "*(self.rect[2]-2)
        bar_text_array=list(bar_text)
        center_x=(self.rect[2]-2)//2
        #scaled_x=3
        #so everything up to 
        if scaled_x>0:
            scaled_x=min(scaled_x,(self.rect[2]-2)//2-1)
            for i in range(0,int(scaled_x)):
                bar_text_array[center_x+i]="█"
            remainder=scaled_x-int(scaled_x)
            bar_text_array[int(center_x+scaled_x)]=map_val_to_fill(remainder)
        else:
            scaled_x=max(scaled_x,-(self.rect[2]-2)//2)
            for i in range(int(center_x+scaled_x),center_x):
                bar_text_array[i]="█"
            remainder=scaled_x-int(scaled_x)
            bar_text_array[int(center_x+scaled_x)]=map_val_to_fill(-remainder)

        bar_text="".join(bar_text_array)
        center_y=self.rect[1]+(self.rect[3]+1)//2
        print(term.move_xy(self.rect[0]+1,center_y)+bar_text,end="",flush=True)
        tics_text=" "*(self.rect[2]-2)
        tics_text_array=list(tics_text)
        left_label="|{:.1f} {}".format(self.bounds[0],self.units)
        right_label="{:.1f} {}|".format(self.bounds[1],self.units)
        for i in range(0,len(left_label)):
            tics_text_array[i]=left_label[i]
        for i in range(0,len(right_label)):
            tics_text_array[-1-i]=right_label[-1-i]
        tics_text_array[center_x]="┼"
        tics_text="".join(tics_text_array)
        print(term.move_xy(self.rect[0]+1,center_y+1)+tics_text,end="",flush=True)
        self.content_dirty=False

class TimeGraph(BorderedTile):
    def __init__(self,rect=(0,0,0,0),title="",bounds=(0,1),y_units="V",x_labels=("","")):
        super().__init__(rect,title=title)
        self.rect=rect
        self.data=[]
        self.max_data_points=self.rect[2]-2
        self.y_bounds=bounds
        self.y_units=y_units #Not used
        self.x_labels=x_labels
        self.content_dirty=True

    def add_data_point(self,data_point):
        self.data.append(data_point)
        if len(self.data)>self.max_data_points:
            self.data=self.data[1:]
        self.content_dirty=True

    def draw(self,term):
        super().draw(term)
        if not self.content_dirty:
            return
        for i in range(0,self.rect[3]-3):
            char_array=[]
            for j in range(0,len(self.data)):
                y=(self.rect[3]-3.0)*(self.data[j]-self.y_bounds[0])/(self.y_bounds[1]-self.y_bounds[0])
                char_array.append(map_val_to_vblock(y-i))
            print(term.move_xy(self.rect[0]+1,self.rect[1]+self.rect[3]-i-2)+"".join(char_array),end="",flush=True)
        x_label_array=list(" "*(self.rect[2]-2))
        for i in range(len(self.x_labels[0])):
            x_label_array[i]=self.x_labels[0][i]
        for i in range(len(self.x_labels[1])):
            x_label_array[-1-i]=self.x_labels[1][-1-i]
        print(term.move_xy(self.rect[0]+1,self.rect[1]+self.rect[3]-1)+"".join(x_label_array),end="",flush=True)
        self.content_dirty=False      
        
        
