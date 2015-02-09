## Create LDAVis from topik output data.
  
  read.matrix.mart <- function(mtx.file, as.sparse=TRUE) {
    mtx.file <- as.character(mtx.file[1L])
    as.sparse <- as.logical(as.sparse[1L])

    mtx <- read.table(mtx.file, header=FALSE, comment.char="%")
    nr <- mtx[1,1]
    nc <- mtx[1,2]
    nnz <- mtx[1,3]
    mtx <- mtx[-1, ]
    rows <- mtx[, 1] - 1L
    cols <- mtx[, 2] - 1L
    vals <- as.numeric(mtx[, 3])

    out <- new("dgTMatrix", x=vals, i=rows, j=cols, Dim=c(nr, nc))
    out
  }

  library("LDAvis")
  library("Matrix")
  library("data.table")
  r_dir <- Sys.getenv("LDAVIS_DIR")
  setwd(r_dir)
  theta_mm <- read.matrix.mart('docTopicProbMat.mm')
  theta <- as.matrix(theta_mm)
  
  phi <- as.matrix(fread('topicTermDist', header = F, sep = ','))
  
  doc.length <- scan("doc_length")
  doc.length <- as.vector(doc.length)
  term_frequency <- scan("term_frequency")
  vocab <- fread('vocab', header = F, sep = '\n')$V1

  phi_n <- sweep(phi, 1, rowSums(phi), FUN="/")
  theta_n <- sweep(theta, 1, rowSums(theta), FUN="/")
  
  create_json <- createJSON(phi=phi_n, theta = theta_n, doc.length = doc.length, vocab=vocab, term.frequency=term_frequency)
  
  serVis(create_json, out.dir='./output',  open.browser = FALSE)
  
