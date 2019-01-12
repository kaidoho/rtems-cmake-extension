
#if defined( TEST_PRIxPTR )
  #include <inttypes.h>
  #include <stdio.h>

  uintptr_t ptr = 42;
  printf("%" PRIxPTR "\n", ptr);
#endif

#if defined( TEST_PRIuPTR )
#include <inttypes.h>
#include <stdio.h>

uintptr_t ptr = 42;
printf("%" PRIuPTR "\n", ptr);
#endif

#if defined( TEST_PRIdPTR )
  #include <inttypes.h>
  #include <stdio.h>

  intptr_t ptr = -1;
  printf("%" PRIdPTR "\n", ptr);
#endif

#if defined( PRINTF_ZU_SIZE_T )
  #include <sys/types.h>
  #include <stdio.h>

  size_t sz = 1;
  printf("%zu\n", sz);
#endif


#if defined( PRINTF_ZD_SSIZE_T )
  #include <sys/types.h>
  #include <stdio.h>

  ssize_t sz = 1;
  printf("%zd\n", sz);
#endif

#if defined( PRINTF_LD_OFF_T )
  #include <sys/types.h>
  #include <stdio.h>

  off_t off = 1;
  printf("%ld\n", off);
#endif

#if defined( PRINTF_LD_OFF_T )
  #include <sys/types.h>
  #include <stdio.h>

  off_t off = 1;
  printf("%lld\n", off);
#endif
