import numpy as np, subprocess, sys, math
from PIL import Image, ImageDraw
out, s_bolt, s_ruler, v, th = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
W,H=1280,720; FPS=240; g=9.81
rng=np.random.default_rng(1)
yy,xx=np.mgrid[0:H,0:W]
bg=(190+20*np.sin(xx/300.0)+8*(yy/H)).astype(np.float32)
base=bg.copy()
# yardstick (tan) on the wall for realism
base[330:360, 300:int(300+s_ruler*914.4)]=150
vx=v*math.cos(math.radians(th)); vy=v*math.sin(math.radians(th))
L=104*s_bolt; T=8*s_bolt
cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','gray','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',out]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
x0,y0=150.0,300.0
for f in range(400):
    img=base.copy()
    n=f-180
    if 0<=n<45:
        acc=np.zeros((H,W),np.float32); sub=6
        for k in range(sub):
            tt=(n+(k/sub-0.5)*0.5)/FPS      # exposure = half a frame
            X=x0+vx*1000*tt*s_bolt; Y=y0-(vy*1000*tt-0.5*g*1000*tt*tt)*s_bolt
            vyy=vy-g*tt; ang=math.atan2(-vyy,vx)
            c,s=math.cos(ang),math.sin(ang)
            pts=[(X+(-L/2)*c-(-T/2)*s, Y+(-L/2)*s+(-T/2)*c),(X+(L/2)*c-(-T/2)*s, Y+(L/2)*s+(-T/2)*c),(X+(L/2)*c-(T/2)*s, Y+(L/2)*s+(T/2)*c),(X+(-L/2)*c-(T/2)*s, Y+(-L/2)*s+(T/2)*c)]
            im=Image.new('L',(W,H),0);ImageDraw.Draw(im).polygon(pts,fill=255)
            acc+=np.asarray(im,np.float32)/255.0/sub
        img=img*(1-acc)+15*acc
    img+=rng.normal(0,2.0,img.shape).astype(np.float32)
    p.stdin.write(np.clip(img,0,255).astype(np.uint8).tobytes())
p.stdin.close();p.wait()
print('wrote',out)
