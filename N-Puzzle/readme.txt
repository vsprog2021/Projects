Necesar:
1) IntelliJ pentru Java
2) Libraria CLIPS.JNI de aici: 
https://sourceforge.net/projects/clipsrules/files/CLIPS/6.40/clips_jni_640.zip/download
4) Unzip la clips_jni_640.zip si apoi adaugare la librariile din project (File -> Project Structure -> libraries (folderul rezultat dupa unzip)
3) CLIPSDOS

Cum se ruleaza:
1) Run la ClipsRunner.java (din IntelliJ)
2) Start
3) Alege size-ul (intre 2 si 5, poate fi modificat maximul (5) la linia asta: new SpinnerNumberModel(2, 2, 5, 1)
4) Alegerea elementelor pentru n-puzzle, intai alegem cifra/numarul apoi apasam pe oricare din cele doua "*"
5) Alegem size^2 numar de elemente, adica pentru 9 elemente (8-puzzle mai exact) vom avea 3x3, adica size=3
6) In fisierul input-size se va afla size-ul dat de la spinner-ul din java
7) In fisierul input-board se va afla lista de elemente date de la Calculator din java (lista pentru n-puzzle)
8) In fisierul output se va afla rezultatul, mai multe linii care descriu problem si care ofera solutia

Mentiuni:
1) Folosim BFS deci multe solutii nu vor fi gasite deoarece numarului mare de cautari
2) Puteti folosi stari.txt pentru niste exemple care arata cum functioneaza
3) Proiectul in java ar trebui a fie: language = Java, Build System = IntelliJ
4) Trebuie schimbate:
a) In java:
	new FileWriter("C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-size.txt")
	new FileWriter("C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-board.txt")
	new FileWriter("C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-board.txt", true)
	clips.load("c:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\Proiect_N-Puzzle-Java.clp")
b) In clips:
	(bind ?fisier-input-size "C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-size.txt")
	(bind ?fisier-input-board "C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-board.txt")
	(bind ?fisier-output "C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\output.txt")
	