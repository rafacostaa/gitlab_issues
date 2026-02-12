#!/usr/bin/env python3
"""
Script ULTRA-RÁPIDO para deletar issues do GitLab via API
Versão 3: Com processamento paralelo (threads) para máxima velocidade
"""

import requests
import json
from typing import List, Dict, Optional
import time
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


class GitLabIssueDeleterFast:
    def __init__(self, gitlab_url: str, private_token: str, project_id: str, verify_ssl: bool = True):
        """
        Inicializa o deletador de issues

        Args:
            gitlab_url: URL base do GitLab
            private_token: Token de acesso pessoal com permissões de API
            project_id: ID do projeto (número ou namespace/projeto)
            verify_ssl: Verificar certificado SSL
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.private_token = private_token
        self.project_id = quote_plus(
            project_id) if '/' in project_id else project_id
        self.project_id_raw = project_id
        self.verify_ssl = verify_ssl
        self.headers = {
            'PRIVATE-TOKEN': private_token,
            'Content-Type': 'application/json'
        }
        self.api_base = f"{self.gitlab_url}/api/v4"

        # Lock para print thread-safe
        self.print_lock = Lock()

        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _make_request_with_retry(self, method: str, url: str, max_retries: int = 3, **kwargs):
        """Faz requisição com retry automático"""
        for attempt in range(max_retries):
            try:
                response = requests.request(method, url, **kwargs)
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                else:
                    raise

    def get_project_info(self) -> Dict:
        """Obtém informações do projeto"""
        url = f"{self.api_base}/projects/{self.project_id}"
        response = self._make_request_with_retry(
            'GET', url, headers=self.headers, verify=self.verify_ssl)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro: {response.status_code} - {response.text}")

    def list_issues_by_id_range(self, start_iid: int, end_iid: int) -> List[Dict]:
        """Lista issues em um intervalo de IDs (com threads para velocidade)"""
        issues = []
        print(f"🔍 Buscando issues de #{start_iid} até #{end_iid}...")

        def fetch_issue(iid):
            try:
                url = f"{self.api_base}/projects/{self.project_id}/issues/{iid}"
                response = self._make_request_with_retry('GET', url, headers=self.headers,
                                                         verify=self.verify_ssl, max_retries=2)
                if response.status_code == 200:
                    return response.json()
            except:
                pass
            return None

        # Busca em paralelo com threads
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(fetch_issue, iid): iid for iid in range(
                start_iid, end_iid + 1)}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                if result:
                    issues.append(result)

                if i % 100 == 0:
                    print(
                        f"  Progresso: {i}/{end_iid-start_iid+1} verificadas, {len(issues)} encontradas")

        print(f"✓ Total encontradas: {len(issues)} issues")
        return issues

    def list_issues_by_filter(self, labels: Optional[List[str]] = None,
                              created_after: Optional[str] = None,
                              created_before: Optional[str] = None,
                              state: str = 'opened',
                              max_pages: int = 100) -> List[Dict]:
        """Lista issues com filtros específicos via API"""
        issues = []
        page = 1

        params = {
            'state': state,
            'per_page': 100,
            'order_by': 'created_at',
            'sort': 'asc'
        }

        if labels:
            params['labels'] = ','.join(labels)
        if created_after:
            params['created_after'] = f"{created_after}T00:00:00Z"
        if created_before:
            params['created_before'] = f"{created_before}T23:59:59Z"

        print(f"🔍 Buscando issues com filtros...")

        while page <= max_pages:
            params['page'] = page

            try:
                url = f"{self.api_base}/projects/{self.project_id}/issues"
                response = self._make_request_with_retry('GET', url, headers=self.headers,
                                                         params=params, verify=self.verify_ssl)

                if response.status_code != 200:
                    break

                page_issues = response.json()
                if not page_issues:
                    break

                issues.extend(page_issues)
                print(
                    f"  Página {page}: +{len(page_issues)} issues (Total: {len(issues)})")

                page += 1
                time.sleep(0.1)

            except Exception as e:
                print(f"⚠️  Erro na página {page}: {e}")
                break

        print(f"✓ Total encontradas: {len(issues)} issues")
        return issues

    def delete_issue(self, issue_iid: int) -> tuple[bool, int]:
        """Deleta uma issue e retorna (sucesso, iid)"""
        url = f"{self.api_base}/projects/{self.project_id}/issues/{issue_iid}"

        try:
            response = self._make_request_with_retry('DELETE', url, headers=self.headers,
                                                     verify=self.verify_ssl, max_retries=2)
            return (response.status_code == 204, issue_iid)
        except:
            return (False, issue_iid)

    def delete_issues_parallel(self, issue_iids: List[int], max_workers: int = 10) -> Dict:
        """
        Deleta issues em PARALELO usando threads

        Args:
            issue_iids: Lista de IDs das issues
            max_workers: Número de threads paralelas (5-20 recomendado)

        Returns:
            Estatísticas de deleção
        """
        stats = {
            'success': 0,
            'failed': 0,
            'total': len(issue_iids),
            'failed_iids': []
        }

        print(
            f"🚀 Deletando {len(issue_iids)} issues com {max_workers} threads paralelas...")
        print(
            f"⏱️  Tempo estimado: ~{len(issue_iids) / (max_workers * 2):.0f} segundos")
        print()

        start_time = time.time()
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submete todas as tarefas
            futures = {executor.submit(
                self.delete_issue, iid): iid for iid in issue_iids}

            # Processa conforme completam
            for future in as_completed(futures):
                success, iid = future.result()
                completed += 1

                if success:
                    stats['success'] += 1
                    status = "✓"
                else:
                    stats['failed'] += 1
                    stats['failed_iids'].append(iid)
                    status = "✗"

                # Print a cada 50 issues ou no final
                if completed % 50 == 0 or completed == stats['total']:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    remaining = (stats['total'] - completed) / \
                        rate if rate > 0 else 0

                    with self.print_lock:
                        print(f"[{completed}/{stats['total']}] "
                              f"✓ {stats['success']} | ✗ {stats['failed']} | "
                              f"⚡ {rate:.1f}/s | "
                              f"⏱️  {remaining:.0f}s restantes")

        elapsed_total = time.time() - start_time
        print(
            f"\n⏱️  Tempo total: {elapsed_total:.1f} segundos ({elapsed_total/60:.1f} minutos)")

        return stats


def main():
    """Script principal"""

    print("=" * 70)
    print("🚀 GitLab Issue Deleter v3 ULTRA-RÁPIDO - Deleção Paralela")
    print("=" * 70)
    print()

    # Configurações
    print("⚙️  Configuração da conexão\n")
    GITLAB_URL = input("URL base: ").strip() or "https://gitlab.gruporefit.com"
    PRIVATE_TOKEN = input("Token: ").strip()
    PROJECT_ID = input("Projeto: ").strip() or "grupofit-dev/portal-sistemas"

    verify_ssl_input = input("Verificar SSL? (s/N) [N]: ").strip().lower()
    verify_ssl = verify_ssl_input == 's'

    workers_input = input("Threads paralelas (5-20) [10]: ").strip()
    max_workers = int(workers_input) if workers_input else 10

    print()

    try:
        deleter = GitLabIssueDeleterFast(
            GITLAB_URL, PRIVATE_TOKEN, PROJECT_ID, verify_ssl)

        # Info do projeto
        print("📊 Obtendo informações do projeto...")
        project_info = deleter.get_project_info()
        print(f"✓ Projeto: {project_info['name_with_namespace']}")
        print(
            f"  Issues abertas: {project_info.get('open_issues_count', 'N/A')}")
        print()

        # Loop principal - permite múltiplas operações sem re-preencher dados
        while True:
            # Método de seleção - com loop para não perder os dados
            issues_to_delete = []

            while True:
                print("🎯 Como selecionar as issues?\n")
                print("1 - Intervalo de IDs (ex: 1001-36000)")
                print("2 - Filtros (labels, datas)")
                print("3 - UMA issue específica")
                print("0 - Cancelar")
                print()

                method = input("Escolha: ").strip()

                if method == '0':
                    print("Cancelado.")
                    return

                elif method == '1':
                    print("\n📋 Intervalo de IDs\n")
                    start_iid = int(input("ID inicial: ").strip())
                    end_iid = int(input("ID final: ").strip())

                    # SEMPRE oferece opção rápida
                    quick = input(
                        "\n⚡ Deletar diretamente SEM buscar (mais rápido)? (S/n) [S]: ").strip().lower()

                    if quick != 'n':
                        # MODO RÁPIDO: Cria lista de IDs sem buscar (muito mais rápido!)
                        issues_to_delete = [{'iid': i}
                                            for i in range(start_iid, end_iid + 1)]
                        print(
                            f"✓ {len(issues_to_delete)} IDs selecionados para deleção rápida")
                    else:
                        # MODO LENTO: Busca cada issue primeiro (só para ver preview)
                        print("⚠️  Modo lento: buscando issues para preview...")
                        issues_to_delete = deleter.list_issues_by_id_range(
                            start_iid, end_iid)

                    break  # Sai do loop de seleção

                elif method == '2':
                    print("\n🔍 Filtros\n")
                    labels_input = input(
                        "Labels (separadas por vírgula): ").strip()
                    labels = [l.strip() for l in labels_input.split(',')
                              ] if labels_input else None

                    created_after = input(
                        "Criadas após (YYYY-MM-DD): ").strip() or None
                    created_before = input(
                        "Criadas antes (YYYY-MM-DD): ").strip() or None

                    state = input(
                        "Estado (opened/closed/all) [all]: ").strip() or 'all'
                    max_pages = int(
                        input("Máx. páginas [100]: ").strip() or '100')

                    print()
                    issues_to_delete = deleter.list_issues_by_filter(
                        labels=labels,
                        created_after=created_after,
                        created_before=created_before,
                        state=state,
                        max_pages=max_pages
                    )
                    break  # Sai do loop de seleção

                elif method == '3':
                    iid = int(input("\nID da issue: ").strip())
                    print(f"\n🗑️  Deletando #{iid}...")
                    success, _ = deleter.delete_issue(iid)
                    print("✓ Deletada!" if success else "✗ Falhou")

                    # Pergunta se quer continuar
                    print()
                    continuar = input(
                        "🔄 Deletar mais issues? (S/n) [S]: ").strip().lower()
                    if continuar == 'n':
                        print("\n✅ Script finalizado!")
                        return

                    # Atualiza info e reinicia
                    print("\n📊 Atualizando informações do projeto...")
                    project_info = deleter.get_project_info()
                    print(
                        f"  Issues restantes: {project_info.get('open_issues_count', 'N/A')}")
                    print()
                    continue  # Volta ao início do loop principal

                else:
                    print("\n❌ Opção inválida! Escolha 0, 1, 2 ou 3.\n")
                    # Loop continua, não sai do script

            # Preview
            print(f"\n📊 Issues selecionadas: {len(issues_to_delete)}\n")

            if not issues_to_delete:
                print("Nenhuma issue encontrada!")
                continue  # Volta ao início do loop principal

            # Preview resumido
            if len(issues_to_delete) <= 20:
                for issue in issues_to_delete[:20]:
                    title = issue.get('title', 'N/A')[:60]
                    print(f"  #{issue['iid']}: {title}")
            else:
                print(
                    f"  IDs: #{issues_to_delete[0]['iid']} até #{issues_to_delete[-1]['iid']}")

            # Confirmação
            print("\n" + "=" * 70)
            print("⚠️  ATENÇÃO: Operação IRREVERSÍVEL!")
            print("=" * 70)
            confirm = input(
                f"\nDeletar {len(issues_to_delete)} issues? Digite 'SIM': ").strip()

            if confirm.upper() != 'SIM':
                print("\n❌ Cancelado.")
                continue  # Volta ao início do loop principal ao invés de sair

            # DELETAR!
            print()
            issue_iids = [issue['iid'] for issue in issues_to_delete]
            stats = deleter.delete_issues_parallel(
                issue_iids, max_workers=max_workers)

            # Resultados
            print("\n" + "=" * 70)
            print("📈 RESULTADOS FINAIS:")
            print(f"  Total: {stats['total']}")
            print(
                f"  ✓ Sucesso: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
            print(f"  ✗ Falhas: {stats['failed']}")

            if stats['failed_iids']:
                print(f"\n  IDs falhados: {stats['failed_iids'][:50]}")
                if len(stats['failed_iids']) > 50:
                    print(f"  ... e mais {len(stats['failed_iids']) - 50}")

            print("=" * 70)

            # Pergunta se quer continuar deletando
            print()
            continuar = input(
                "🔄 Deletar mais issues? (S/n) [S]: ").strip().lower()

            if continuar == 'n':
                print("\n✅ Script finalizado!")
                return

            # Atualiza info do projeto antes de continuar
            print("\n📊 Atualizando informações do projeto...")
            project_info = deleter.get_project_info()
            print(
                f"  Issues restantes: {project_info.get('open_issues_count', 'N/A')}")
            print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
