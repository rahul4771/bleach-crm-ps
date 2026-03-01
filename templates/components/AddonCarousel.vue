<template>
  <div class="col-md-12 mt-2" v-if="addons.length > 0">
    <div :class="wrapperClass">
      <div class="service-content-heading">{{ heading }}</div>
      <div style="padding-left: 32px; padding-right: 32px;">
        <div class="owl-carousel other-service-carousel" :id="carouselId">
          <addon-card 
            v-for="(addon, index) in addons" 
            :key="index"
            :addon="addon" 
            :index="index"
            @select="$emit('select', $event)"
            @reduce="$emit('reduce', $event)"
            @increase="$emit('increase', $event)"
            @update-quantity="$emit('update-quantity', $event)"
            @choose-size="$emit('choose-size', $event)">
          </addon-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddonCarousel',
  props: {
    addons: {
      type: Array,
      required: true,
      default: () => []
    },
    carouselId: {
      type: String,
      required: true
    },
    heading: {
      type: String,
      default: 'Add-ons'
    },
    wrapperClass: {
      type: String,
      default: 'more-services'
    }
  },
  watch: {
    addons: {
      handler() {
        this.reinitializeCarousel();
      },
      deep: true
    }
  },
  mounted() {
    this.reinitializeCarousel();
  },
  methods: {
    reinitializeCarousel() {
      setTimeout(() => {
        this.$nextTick(() => {
          const selector = `#${this.carouselId}`;
          const $carousel = $(selector);

          if ($carousel.length === 0) return;

          $carousel.css({ 'opacity': '0', 'transition': 'opacity 0.1s' });

          if ($carousel.hasClass('owl-loaded')) {
            $carousel.trigger('destroy.owl.carousel').removeClass('owl-loaded owl-drag owl-carousel');
            $carousel.find('.owl-stage-outer, .owl-stage, .owl-item, .owl-nav, .owl-dots').remove();
          }

          const finalItemsCount = $carousel.children().length;

          if (finalItemsCount > 0) {
            $carousel.addClass('owl-carousel').owlCarousel({
              items: 4,
              loop: false,
              margin: 10,
              nav: true,
              dots: false,
              responsive: {
                0: { items: 1 },
                600: { items: 2 },
                1000: { items: 4 }
              }
            });

            setTimeout(() => {
              $carousel.css('opacity', '1');
            }, 50);
          }
        });
      }, 150);
    }
  }
};
</script>
