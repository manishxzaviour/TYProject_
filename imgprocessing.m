figure;
a=imread('capture5.jpg');
b=rgb2gray(a);
d=imcomplement(b);
c=imcrop(d,[150 80 700 320]);
aa=fspecial('unsharp');
cn=imfilter(imfilter(c,aa),aa);
a1=wiener2(cn,[5,5]);
BW = edge(cn,'canny');
[H,T,R] = hough(BW);
P  = houghpeaks(H,5);
x = T(P(:,2)); 
y = R(P(:,1));
plot(x,y,'s','color','green');
lines = houghlines(BW,T,R,P);
subplot(2,2,3);
pq=edge(a1,'canny');
pq=imcrop(pq,[60 10 600 300]);
[yn,xn]=size(pq);
imshow(pq), hold on
for k = 1:length(lines)
    xy = [lines(k).point1; lines(k).point2];
    plot(xy(:,1),xy(:,2),'LineWidth',2,'Color','green');
    plot(xy(1,1),xy(1,2),'x','LineWidth',2,'Color','yellow');
    plot(xy(2,1),xy(2,2),'x','LineWidth',2,'Color','red'); 
end
title('edges [hough+canny]');
i=0;
p=0;
subplot(224);
imshow(pq), hold on
for k = 1:length(lines)
    xy = [lines(k).point1; lines(k).point2];
    if xy(1,2)>50&&xy(1,2)<300&&xy(2,2)>50&&xy(2,2)<300
        p=p+(xy(1,2)+xy(2,2))/2;
        i=i+1;
    end
end
line=p/i;
plot([0,xn],[line,line],'LineWidth',2,'Color','green');
for j=1:yn
    for k=1:xn
        if pq(j,k)==1
            if abs(j-line)>60
                plot(k,j,'.','LineWidth',1,'Color','red');
            end
        end
    end
end
title("detection");
subplot(221);imshow(c);title("original");
subplot(222);imshow(a1);title("enhanced");


