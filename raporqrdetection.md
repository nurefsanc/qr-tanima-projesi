# Proje Raporu

## İmport Pyzbar
* Önce pyzbar isimli ana kütüphane klasörüne gidip klasörün içindeki pyzbar.py isimli dosyayı bulundu ve dosyanın içindeki decode fonksiyonunu alındı. Decode fonksiyonu resimdeki siyah-beyaz karelerin dizilişine bakar, QR kod algoritmasını uygular.
* 'cv2.VideoCapture(0)' ile webcam açılımı sağlandı
* ret değişkeni ile kamera açılmaması durumunda programın çökmesini engellendi.

## Görüntünün Geometrisi
* .shape matrisin boyutlarını verir. (Yükseklik, genişlik, temel renk katmanlarının (kanal) sayısı). _ kullanarak ihtiyaç olmadığı için kanallar ihmal edildi.

## Kamera Matrisi
* focal_length = w odak uzaklığıdır, zoom miktarını belirler. "Odak uzaklığı yaklaşık resim genişliği kadardır" varsayımı yapılır. Bu, standart bir Webcam'in yaklaşık 60 derecelik görüş açısına denk gelir ve işimizi görür.
* center_x ve center_y Lensin tam ortasından geçen ışığın, resim üzerinde düştüğü piksel koordinatıdır. İdeal bir kamerada lens tam ortadadır. Bu yüzden resmin genişliğinin (w) ve yüksekliğinin (h) tam yarısı merkez kabul edildi.
* camera_matrix = np.array -> np.array, verileri hafızada C++'ın anlayabileceği şekilde (bitişik, düzenli ve tek tipte) tutar. 
* np.array'ın içine sırasıyla uzaydaki x,y,z koordinatlarını ekrandaki piksele çevirmek için değerler yazıldı.
* OpenCV C++ tarafında işlem yaparken 32 bitlik ondalıklı sayı ister o yüzden np.array dtype=np.float32 yazıldı.
* dist_coeffs = np.zeros((4, 1)) kamera kalibrasyonu yapmadan hızlı bir şekilde ışığın bükülmesini ihmal ederek kamerayı mükemmel kabul ettik.

## QR Kod Modeli Tanımlama
* Birim olarak bir kenar uzunluğu tanımlandı, her bir köşenin koordinatı yazıldı. 32 bitlik sayı haline getirildi.
* Burada 3 boyutlu uzayda 4 tane stratejik nokta belirlenip çizgilerin uç noktaları tanımlandı.

## Görüntü Okuma ve QR Tespit
* Görüntünün alınabilirliğinin kontrolü yapıldı.
* decoded_objects = decode(frame) fotoğrafın her pikselini tarayıp qr'ı arar, bulamazsa da boş liste olarak döner.
* for döngüsü ile ekrandaki her bir qr'a sırası ile bakılıp okunan metni temiz halde ekrana yazdırıldı.

## Bounding Box
* pts = image_points.astype(np.int32): Bilgisayar ekranındaki pikseller tam sayıdır, bu kod ondalıklı sayıları en yakın tam sayıya çevirir. Çizim fonksiyonları (OpenCV) bunu şart koşar.
* Polylines fonksiyonu aynı anda binlerce noktayı hiç takılmadan, çok hızlı bir şekilde işlemesini sağlar. Çalışabilmesi için de noktaları fonksiyonun istediği matris şeklinde vermemiz gerekir, reshape de bunu sağlar. 
* Polyline fonksiyonunda içeriye sırasıyla Üzerine çizim yapılacak olan o anki kamera görüntüsü, çizilecek köşe noktaları, son noktayı ilk noktaya bağlayarak tam bir kare/dikdörtgen oluşturması için true, renk kodu, çizginin kalınlığı girilir.

## Konum ve Açı
* solvePnP fonksiyonu "Perspektif ve Noktalar" probleminin çözümüdür. Arka planda matematiksel olarak "Elimdeki kareyi (object), uzayda nasıl döndürürsem ve ne kadar uzağa koyarsam, kamerada tam olarak şu an gördüğüm yamuk şekli (image) oluşturur?" sorusunu çözer. 
* Bunları da içine sırasıyla object_points bilgisayara nesnenin aslında nasıl olması gerektiğini (dümdüz bir kare) söylediğimiz 3D referans haritasıdır. image_points kameranın o an gerçekten ne gördüğünü söylediğimiz 2D ekran verisidir. camera_matrix bilgisayara kameranın ne kadar zoom yaptığı ve merkezinin neresi olduğunu söylediğimiz verilerdir. dist_coeffs kamera lensindeki cam eğriliklerini bilgisayara bildirdiğimiz düzeltme sayılarıdır. 
* Sonucunda fonksiyon bize success: Hesaplama başarılı oldu mu? (True/False). rvec: QR kodun kendi etrafında nasıl döndüğünü anlatır, Bu vektör, 3 eksendeki (X, Y, Z) eğim açılarını içerir. tvec: QR kodun kameraya göre nerede olduğunu söyler.

## Eksenleri Ekranda Gösterme
* Qr kodun kameradan uzaklığına bağlı olarak öncesinde bizim verdiğimiz orana göre uç noktaları ekrandaki hangi piksele denk gelir hesaplanır. Pixseller buçuklu olamayacağı ve çizim yapılamayacağı için tam sayıya çevirilir. 
* center: qr kodun merkezi tanımlanır. ravel komutu ile veriler iç içe matris halinden düzmdüz hale getirilir.
* cv2.line(...) Komutları iki nokta arasına düz bir çizgi çekmek için kullanılır. Sırasıyla merkezden başlayıp farklı renklerde her bir eksenin ucuna gitmek için kullanıldı.
* cv2.putText resme yazı koyma fonksiyonu. Yazıyı qr kodun sol üstüne hizalayıp biraz yukarı kaydırdık. Font, boyut ve renk de eklendi. 