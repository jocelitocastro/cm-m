# cm-m
## Crop Models modules

Para execução python em shell ou powershell.

Parte de minha tese de doutorado para geração de dados de entrada e cenários do CropSyst.

Contribuições são importantes. As aplicações podem ser estendidas para outros modelos.


## Geração da grade regular

- Exemplo dos parâmetros para chamada do módulo:

xmin = -53
xmax = -51
ymin = -25
ymax = -24
res_y = 0.1
res_x = 0.1
dem_raster_file = raster_dem_file_name.tif

- Gerar a grade regular 

Comando:
```
python .\1_grade.py -53 -51 -25 -24 0.1 0.1 dem_PR_4326_ASTER.tif
```

## Geração dos arquivos de solos

- Baixar os mapas do SoilGrids

Comando:

python .\2_baixar_mapas_soilgrids.py

- Gerar os parâmetros físico-hídricos e arquivos de solo

Comando:

python .\3_gerar_arquivos_solo.py


## Geração dos arquivos climáticos

- Baixar os arquivos da grade de Xavier

Comando:

python .\4_baixar_grade_Xavier.py

- Gerar os arquivos climáticos

Comando:

python .\5_criar_arquivos_ued_.py


## Geração dos arquivos de configuração de cultura

- Exemplo dos parâmetros para chamada do módulo:

Início da rotação = 1961

Fim da rotação = 2019

Primeiro dia juliano de semeadura = 150

Último dia juliano de semeadura = 200

Intervalo de semeadura (dias) = 10

- Gerar os cenários de cultura

Comando:

python .\6_criar_cenarios.py 1961 2019 150 200 10