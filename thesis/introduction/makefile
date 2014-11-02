LATEXMK		=	latexmk
TARGET		=	introduction_talk


pdf:
	$(LATEXMK) -f -pdf $(TARGET)
	xdg-open $(TARGET).pdf

cont:
	$(LATEXMK) -f -silent -pvc -pdf $(TARGET)

clean:
	$(LATEXMK) -c && rm -rf $(TARGET).bbl $(TARGET)-blx.bib $(TARGET).run.xml
	rm -rf *.bak
