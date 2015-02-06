##' Reads in data in matrix market format
##'
##' Warning: This is slow.
##'
##' TODO: Wrap matrix market C code (mmio.{h|c})
##'
##' @param mtx.file The path to the matrix market file
##' @return A (dense) matrix

read.matrix.mart <- function(mtx.file, as.sparse=TRUE, use.c=FALSE) {
  mtx.file <- as.character(mtx.file[1L])
  as.sparse <- as.logical(as.sparse[1L])
  use.c <- as.logical(use.c[1L])

  stopifnot(file.exists(mtx.file))

  if (use.c) {
    # stop("TODO: Need to fix memory not mapped errors when reading banner")
    ret <- .Call("read_matrix_market", mtx.file, as.sparse, PACKAGE="buckshot")
    nr <- ret$nrows
    nc <- ret$ncols
    rows <- ret$rows
    cols <- ret$cols
    vals <- ret$vals
    nnz <- length(rows)
  } else {
    mtx <- read.table(mtx.file, header=FALSE, comment.char="%")
    nr <- mtx[1,1]
    nc <- mtx[1,2]
    nnz <- mtx[1,3]
    mtx <- mtx[-1, ]
    rows <- mtx[, 1] - 1L
    cols <- mtx[, 2] - 1L
    vals <- as.numeric(mtx[, 3])
  }

  out <- new("dgTMatrix", x=vals, i=rows, j=cols, Dim=c(nr, nc))
  out
}

write.matrix.mart <- function(x, file.name) {
  idxs <- which(x != 0, arr.ind=TRUE)
  outfile <- file(file.name, 'w')
  i <- 1
  N <- nrow(idxs)
  cat("%%MatrixMarket matrix coordinate real general\n", file=outfile)
  cat(sprintf("%d %d %d\n", nrow(x), ncol(x), nrow(idxs)), file=outfile)
  while (i <= N) {
    row <- idxs[i,1]
    col <- idxs[i,2]
    cat(sprintf("%d %d  %f\n", row, col, x[row,col]), file=outfile)
    i <- i + 1
  }
  close(outfile)
}


library("LDAvis")
library("Matrix")

theta_mm <- read.matrix.mart('docTopicProbMat.mm')
theta <- as.matrix(theta_mm)

phi <- as.matrix(fread('topicTermDist', header = F, sep = ','))

doc.length <- scan("doc_length")
doc.length <- as.vector(doc.length)
term_frequency <- scan("term_frequency")
vocab <- fread('vocab', header = F, sep = '\n')

phi_n <- sweep(phi, 1, rowSums(phi), FUN="/")
theta_n <- sweep(theta, 1, rowSums(theta), FUN="/")

create_json <- createJSON(phi=phi_n, theta = theta_n, doc.length = doc.length, vocab=vocab, term.frequency=term_frequency)

serVis(create_json, out.dir='ldavis')

