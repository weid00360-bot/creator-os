# -*- coding: utf-8 -*-
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(11)
OUT=os.path.expanduser("~/Desktop/迪迪视频预览/_通用样张"); os.makedirs(OUT,exist_ok=True)
W,H=1080,1920
CREAM="#F3EFE7"; COBALT="#1F4ED8"; COBALT_D="#163FB0"; RED="#D63737"; INK="#1C1E24"; GRAY="#8A8780"; NAVY="#141A2E"; YEL="#FFD23F"; SCR="#E7E1D4"
HG="/System/Library/Fonts/Hiragino Sans GB.ttc"
def helv(sz):
    try: return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",sz,index=1)
    except: return ImageFont.truetype(HG,sz,index=1)
def fb(s): return ImageFont.truetype(HG,s,index=1)
def fr(s): return ImageFont.truetype(HG,s,index=0)
def Wt(d,xy,t,f,fill,anchor="la"): d.text(xy,t,font=f,fill=fill,anchor=anchor)
def rr(d,b,r,fill=None,outline=None,width=1): d.rounded_rectangle(b,radius=r,fill=fill,outline=outline,width=width)

im=Image.new("RGB",(W,H),CREAM)
grain=Image.new("L",(W,H),0); gd=ImageDraw.Draw(grain)
for _ in range(9000): gd.point((random.randint(0,W-1),random.randint(0,H-1)),fill=random.randint(0,30))
im=Image.composite(Image.new("RGB",(W,H),"#E9E3D6"),im,grain.point(lambda v:int(v*0.5)))
d=ImageDraw.Draw(im)

# header
Wt(d,(60,56),"迪迪.2026",fb(36),INK)
Wt(d,(1020,56),"BUILD IN PUBLIC",helv(32),INK,anchor="ra")
d.line([(60,110),(1020,110)],fill=INK,width=3)
d.ellipse((60,128,76,144),fill=RED); Wt(d,(85,128),"REC",fr(20),GRAY)

# ---- BOLD COBALT TV : tall portrait display window ----
BEZEL=38
Bx1,By1,Bx2,By2=36,200,1044,1300
sx1,sy1,sx2,sy2=Bx1+BEZEL,By1+BEZEL,Bx2-BEZEL,By2-BEZEL   # inner display = embed target
ax=(Bx1+Bx2)//2
# antenna (top)
d.line([(ax-7,By1+4),(ax-112,By1-60)],fill=INK,width=7); d.ellipse((ax-112-11,By1-60-11,ax-112+11,By1-60+11),fill=INK)
d.line([(ax+7,By1+4),(ax+112,By1-66)],fill=INK,width=7); d.ellipse((ax+112-11,By1-66-11,ax+112+11,By1-66+11),fill=INK)
d.polygon([(ax-22,By1+8),(ax+22,By1+8),(ax+12,By1-16),(ax-12,By1-16)],fill=INK)
# cobalt frame + shadow + yellow accent
rr(d,(Bx1+10,By1+12,Bx2+10,By2+12),34,fill="#C9C2B0")
rr(d,(Bx1,By1,Bx2,By2),34,fill=COBALT,outline=INK,width=9)
rr(d,(Bx1+9,By1+9,Bx2-9,By2-9),26,outline=YEL,width=4)
# display slot (empty embed target)
d.rectangle((sx1-6,sy1-6,sx2+6,sy2+6),fill=INK)
d.rectangle((sx1,sy1,sx2,sy2),fill=SCR)
ccx,ccy=(sx1+sx2)//2,(sy1+sy2)//2
d.line([(ccx-30,ccy),(ccx+30,ccy)],fill="#CFC8B8",width=4); d.line([(ccx,ccy-30),(ccx,ccy+30)],fill="#CFC8B8",width=4)
Wt(d,(ccx,ccy-80),"内容 · 落位区",fb(40),"#B7AF9E",anchor="mm")
Wt(d,(ccx,ccy+86),f"{sx2-sx1} × {sy2-sy1}",fr(30),"#C4BCAB",anchor="mm")
for (bx,by,sxn,syn) in [(sx1+24,sy1+24,1,1),(sx2-24,sy1+24,-1,1),(sx1+24,sy2-24,1,-1),(sx2-24,sy2-24,-1,-1)]:
    d.line([(bx,by),(bx+38*sxn,by)],fill="#C7BFAE",width=4); d.line([(bx,by),(bx,by+38*syn)],fill="#C7BFAE",width=4)

# ---- subtitle band ----
sby1,sby2=By2+44,By2+154
for i in range(0,int(960-120),30):
    d.line([(120+i,sby1),(120+i+16,sby1)],fill="#CBC4B4",width=3)
    d.line([(120+i,sby2),(120+i+16,sby2)],fill="#CBC4B4",width=3)

# ---- small avatar bottom-right ----
cx,cy,R=908,1660,108
glow=Image.new("RGBA",(W,H),(0,0,0,0)); gdd=ImageDraw.Draw(glow)
gdd.ellipse((cx-R-20,cy-R-20,cx+R+20,cy+R+20),fill=(31,78,216,165)); glow=glow.filter(ImageFilter.GaussianBlur(24))
im=Image.alpha_composite(im.convert("RGBA"),glow).convert("RGB"); d=ImageDraw.Draw(im)
d.ellipse((cx-R-9,cy-R-9,cx+R+9,cy+R+9),fill="#2E5BE0"); d.ellipse((cx-R,cy-R,cx+R,cy+R),fill=NAVY)
av=Image.new("RGBA",(W,H),(0,0,0,0)); ad=ImageDraw.Draw(av)
hx,hy,hr=cx,cy-5,54
ad.pieslice((cx-90,cy+36,cx+90,cy+230),180,360,fill=COBALT)
ad.line([(cx-23,cy+78),(cx,cy+62),(cx+23,cy+78)],fill=COBALT_D,width=4)
ad.rectangle((hx-14,hy+hr-12,hx+14,hy+hr+22),fill="#EAC9AE")
ad.ellipse((hx-hr,hy-hr,hx+hr,hy+hr),fill="#F4DECA")
ad.chord((hx-hr-2,hy-hr-2,hx+hr+2,hy+hr-10),178,362,fill="#212C52")
ad.ellipse((hx-hr-2,hy-23,hx-hr+16,hy+23),fill="#212C52"); ad.ellipse((hx+hr-16,hy-23,hx+hr+2,hy+23),fill="#212C52")
ad.ellipse((hx-24,hy-2,hx-14,hy+8),fill=INK); ad.ellipse((hx+14,hy-2,hx+24,hy+8),fill=INK)
ad.arc((hx-17,hy+9,hx+17,hy+36),20,160,fill="#7A4A33",width=4)
ad.ellipse((hx-38,hy+12,hx-26,hy+23),fill="#F2B89C"); ad.ellipse((hx+26,hy+12,hx+38,hy+23),fill="#F2B89C")
mask=Image.new("L",(W,H),0); ImageDraw.Draw(mask).ellipse((cx-R+4,cy-R+4,cx+R-4,cy+R-4),fill=255)
clip=Image.new("RGBA",(W,H),(0,0,0,0)); clip.paste(av,(0,0),mask)
im=Image.alpha_composite(im.convert("RGBA"),clip).convert("RGB"); d=ImageDraw.Draw(im)
d.ellipse((cx-R+4,cy-R+4,cx+R-4,cy+R-4),outline="#4E78F0",width=4)
rr(d,(cx-56,cy+R-2,cx+56,cy+R+38),20,fill=COBALT); Wt(d,(cx,cy+R+18),"迪迪",fb(25),"#FFFFFF",anchor="mm")

# ---- title bottom-left ----
def star(px,py,sR,col):
    pts=[(px+math.cos(-math.pi/2+i*math.pi/5)*(sR if i%2==0 else sR*0.42), py+math.sin(-math.pi/2+i*math.pi/5)*(sR if i%2==0 else sR*0.42)) for i in range(10)]
    d.polygon(pts,fill=col)
star(72,1518,13,RED); Wt(d,(94,1505),"AI AGENT 实录",fr(26),COBALT)
Wt(d,(56,1548),"陪跑教练",fb(76),INK)
d.line([(58+i*3.0,1640+math.sin(i/11*math.pi*2)*3) for i in range(108)],fill=RED,width=7,joint="curve")
Wt(d,(58,1672),"not 工具 · 我守判断和审美",fr(29),GRAY)
Wt(d,(58,1864),"CASE SHOW / my build …",helv(24),GRAY)
Wt(d,(1020,1864),"01",fb(28),INK,anchor="ra")

im.save(os.path.join(OUT,"竖版口播背景图_v8.png"))
print("saved v8")
print(f"EMBED_RECT (内容落位, 画布1080x1920): 左上({sx1},{sy1})  尺寸 {sx2-sx1}x{sy2-sy1}  比例≈{(sx2-sx1)/(sy2-sy1):.3f}")
