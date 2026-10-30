# Seguranca, privacidade, segregacao de ambiente e responsabilidade

- **Nao usar dados pessoais reais neste repositorio.** Todos os alunos e IDs são fictícios. Repositórios públicos não recebem logs operacionais, CPF, e-mail, matrícula verdadeira ou exports corporativos.
- **Privilégio mínimo:** perfis distintos para ETL, analistas, suporte e administradores, com aprovação formal.
- **Mascaramento/classificacao:** CPF e PII, se indispensáveis, apenas em ambiente autorizado, com classificação, máscara e controles de acesso por atributo e finalidade.
- **Transportes:** integrações oficiais/TLS, identidade gerenciada, segredos fora do código e trilhas de acesso.
- **Contrato e FIES:** documentos e dados financeiros são sensíveis para finalidade de negócio; a POC nunca tenta acessar sistemas de terceiros ou executar robôs sobre logins de usuários.
- **Auditoria:** metadados técnicos, hashes e lineage ajudam a rastrear transformações, mas não substituem provas jurídicas, assinatura válida ou controles de retenção.
- **Retencao:** definir retenção e descarte com responsáveis pela LGPD, jurídico e TI. Não assumir prazo legal genérico.
- **Sem writeback:** não executar updates/deletes nos legados nesta POC. Correções seguem workflow de aprovação com dono da fonte.
- **Ambientes:** catalogo `vitru_poc_*` exclusivo. Dados de produção nunca são usados em demonstração local.
- **IA:** modelos não precisam ler PII nem escrever medidas oficiais; qualquer resposta analítica passa pela camada semântica governada.
