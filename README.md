# FitMotion

FitMotion é um aplicativo voltado para pessoas que praticam exercícios físicos, especialmente em academias. Utilizando inteligência artificial e a câmera do dispositivo, o aplicativo identifica movimentos realizados em determinados exercícios e gera feedbacks em tempo real, ajudando o usuário a executar os exercícios corretamente.

## Sumário

- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)

## Funcionalidades

- **Feedback em Tempo Real**: Utiliza IA para analisar os movimentos e fornecer correções instantâneas.
- **Planos de Treino Personalizados**: Criação e gerenciamento de rotinas de exercícios alinhadas com os objetivos do usuário.
- **Monitoramento de Progresso**: Acompanhamento do desenvolvimento físico e desempenho ao longo do tempo.
- **Gamificação**: Sistema de conquistas e recompensas para motivar e engajar os usuários.

## Arquitetura

O FitMotion foi desenvolvido utilizando uma arquitetura monolítica, priorizando a simplicidade e a eficiência no desenvolvimento inicial.

![Arquitetura do FitMotion](architecture_image)

### Componentes Principais

- **Frontend**: Interface do usuário responsiva e intuitiva para dispositivos iOS e Android.
- **Módulo de IA**: Modelos de machine learning integrados ao aplicativo para processamento local dos movimentos.
- **Backend**: Servidor responsável pela lógica de negócio e comunicação com serviços externos.
- **Banco de Dados**: Armazenamento de dados em tempo real e autenticação segura.
- **Serviços em Nuvem**: Infraestrutura escalável para hospedagem do backend e serviços auxiliares.

## Tecnologias Utilizadas

- **Flutter**: Framework para desenvolvimento de aplicativos móveis multiplataforma.
- **Python**: Linguagem de programação utilizada no backend.
- **TensorFlow Lite**: Biblioteca para execução de modelos de machine learning em dispositivos móveis.
- **Firebase**: Plataforma para autenticação, banco de dados em tempo real e armazenamento.
- **Google Cloud Platform (GCP)**: Serviços de nuvem para hospedagem e escalabilidade.
- **MediaPipe**: Framework para detecção de poses e reconhecimento de movimentos.
