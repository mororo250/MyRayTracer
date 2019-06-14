# MyRayTracer

## Visão Geral

Essa é uma implementação em python do Ray Tracing in One Weekend encontrado em https://github.com/petershirley/raytracinginoneweekend de Peter SHiley.

## Instruções

### Parametros

Existem 5 possiveis argumentos, os quais todos são opicionais:

1. --resolution ou -r que recebe duas integrais x e y que vão definir a definição da imagem a ser redenrizada. 
      default - 340 480
2. -spp é a quantidade de raios gerados por pixel (samples per pixel). 
      default - 64
3. -scene defini a cena que será renderizada. Existem 4 possiveis cenas: 
      1. basic  - Cena simples para testes e rapidas renderizações.
      2. random - Cena contida na capa do livro do Perer Shirley.
      3. motion - Demonstra a funcionalidade de montion blur.
      4. cube   - Renderiza dois cubos um difuso e outro metalico.
      default - basic
4. --image ou -i endereço relativo da imagem final.
      default - results/image.ppm
5. --threads ou -t numero de processos usados pelo programa.
      default - Numero de cores contidos na sua cpu. 
      
### Recomendações:

Para uma renderização rapida defina um spp menor ao invez de diminuir a resolução. Vai ter um maior impacto na velocidade, ao mesmo tempo que um menor impacto na qualidade da imagem.

Para demonstrar isso foi incluido duas imagens: basic-8spp.ppm e basic-170-240.ppm para demonstração. Foi usada a cena basic sendo a Primeira imagem: Resolução: 340 x 480 / spp: 8
Segunda imagem: Resolucão 170 x 240 / spp: 64 
Os valores foram escolhidos por causa do tempo parecido de execução.

## Implementação:

A implementação é praticamente uma tradução do livro Ray Tracing in One Weekend para python sendo que para as funcionalidades extras 1 e 4 foram usados a sequencia desse livro Ray Tracing: The Next Week. Nesse documento tentarei focar nas diferenças entre as implmentações.

# Multi Threading

Python é uma lingugem muito lenta quando comparada com linguagens de baixo nível com c, c++ ou rust. O que torna uma pessima escolha para implementar um renderer. O processo de desenvolvimento se torna mais lento e penoso, e as mais simples imagens demoram décadas para renderizar. Uma forma de amenizar o problema é utilizar da programação paralela.

Não é correto falar que foi usado multi Threading no programa, pois na realidade é utilizada uma abordadem multi processing. Que possuem algumas diferenças como por exemplo multi processing não compartilha informação e entre o outros. A principal razação de utilizar multi processing é porcausa de uma caracteristica do python chamada xxx que faz com que o multi threading do python funcione em apenas um core, o que definitivamente não resolve o problema de eficiencia do programa. Para contornar esse problema foi utilizada a biblioteca multiprocessing que cria novos processos ao invez de novos threads.

a classe pool que deixa o programa pequeno e limpo:

Codigo:
    pool = multiprocessing.Pool(processes = args.threads)
    results = pool.imap_unordered(partial(doWork, cam = cam, world = world, spp = args.spp, NX = args.resolution[0], NY =       args.resolution[1]), reversed(range(0, args.resolution[1])))
    
    perceba que foi usado imap ao invez de map. A razão disso é que o imap permite interação com os resultados 

