from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pipeline.catalog import build_catalog, import_catalog_review
from pipeline.checklist import build_checklist
from pipeline.common import RunContext, configure_logging
from pipeline.corpus import build_corpus
from pipeline.detect import detect_candidates, import_review
from pipeline.expanded import build_expanded_corpus, discover_sources
from pipeline.outputs import build_outputs
from pipeline.prioritize import import_calibration, prioritize_evidence
from pipeline.snapshot import create_snapshot
from pipeline.sources import enabled_sources

LOGGER = logging.getLogger(__name__)
DEFAULT_RUN_ID = "baseline-2026-05-31"
DEFAULT_AS_OF = "2026-05-31"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline da pesquisa de lacunas de capacitacao no CNJ.")
    parser.add_argument(
        "--step",
        required=True,
        choices=(
            "snapshot",
            "catalog",
            "discover-sources",
            "import-catalog-review",
            "corpus",
            "expanded-corpus",
            "detect",
            "checklist",
            "import-calibration",
            "import-review",
            "prioritize",
            "outputs",
            "sources",
            "all-preliminary",
        ),
    )
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--as-of", default=DEFAULT_AS_OF)
    parser.add_argument("--review-file")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = RunContext.create(run_id=args.run_id, as_of=args.as_of)
    configure_logging(context.paths, args.run_id, verbose=args.verbose)
    LOGGER.info("Executando etapa %s para %s", args.step, args.run_id)
    if args.step == "sources":
        sources = enabled_sources(context.paths.config / "sources.yml")
        LOGGER.info("Registro de fontes carregado: %d entradas", len(sources))
        for source in sources:
            LOGGER.info("- %s | %s | %s", source["name"], source["section"], source["priority"])
    elif args.step == "snapshot":
        create_snapshot(context, force=args.force)
    elif args.step == "discover-sources":
        discover_sources(context, force=args.force)
    elif args.step == "catalog":
        build_catalog(context)
    elif args.step == "import-catalog-review":
        if not args.review_file:
            raise SystemExit("--review-file e obrigatorio para import-catalog-review")
        import_catalog_review(context, Path(args.review_file))
    elif args.step == "corpus":
        build_corpus(context, force=args.force)
    elif args.step == "expanded-corpus":
        build_expanded_corpus(context)
    elif args.step == "detect":
        detect_candidates(context)
    elif args.step == "checklist":
        build_checklist(context)
    elif args.step == "import-calibration":
        if not args.review_file:
            raise SystemExit("--review-file e obrigatorio para import-calibration")
        import_calibration(context, args.review_file)
    elif args.step == "import-review":
        if not args.review_file:
            raise SystemExit("--review-file e obrigatorio para import-review")
        import_review(context, args.review_file)
    elif args.step == "prioritize":
        prioritize_evidence(context)
    elif args.step == "outputs":
        build_outputs(context)
    elif args.step == "all-preliminary":
        create_snapshot(context, force=args.force)
        build_catalog(context)
        build_corpus(context, force=args.force)
        detect_candidates(context)
        build_checklist(context)
        prioritize_evidence(context)
        build_outputs(context)
    LOGGER.info("Etapa %s concluida", args.step)


if __name__ == "__main__":
    main()
